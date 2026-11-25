%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1991,1992.				 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- public translate/0.
:- public translate/2, go/0.

go :- save(pdsstrans), !, translate, halt.

translate :- 
    translate_init,
    write('Debug mode  : '), ttyflush, read(Mode),
    ( Mode == end_of_file, !, error('end_of_file was read', []), halt;
    write('Input file  : '), ttyflush, read(RFile),
    write('Output file : '), ttyflush, read(WFile),
    recorda('$$$Debug$Mode$$$', Mode, REF),
    translate(RFile,WFile),
    erase(REF) ).

translate_init:- recorded('$$$Debug$Mode$$$',_,REF),erase(REF),fail.
translate_init.

deb:- recorded('$$$Debug$Mode$$$',1,_).

:- mode translate(+,+).
translate(RFile,WFile):-
    see(RFile), tell(WFile),
    (trans_and_write_rkp_information(MName),!;
     ttyput(7), ttynl,
     display(' ** Syntax Error in declaration of (module or public) ...'),
     ttynl),
    read(NextProc),
    trans_and_write_all_procedure(MName,NextProc,0,ConstList,[]),
    write_constant_section(MName,ConstList),
    seen, told.
translate(_,_):-
    seen, told.

:- mode trans_and_write_rkp_information(-).
trans_and_write_rkp_information(MName):-
    read(module_information(module(MName),public(Public))),
    write_instr([label(MName),module(MName)]),
    write_entry(Public), !.

:- mode write_entry(+).
write_entry([ProN/Ar|Rest]):- !,
    make_label(ProN/Ar,Lab),
    write_instr(entry(ProN,Ar,Lab)), !,
    write_entry(Rest).
write_entry([]):- !.

:- mode trans_and_write_all_procedure(+,+,+,-,+).
trans_and_write_all_procedure(MName,procedure(ProN,Ar),SN,CL,CLT):-
    write_instr([module_entry(MName),predicate(ProN,Ar)]), !,
    read(NextInstr),
    trans_and_write_one_procedure(NextInstr, NextProc, [], SN,NSN, CL,CL1), !,
    trans_and_write_all_procedure(MName, NextProc, NSN, CL1,CLT).
trans_and_write_all_procedure(_, end_of_file, _, CL, CL).

:- mode trans_and_write_one_procedure(+,-,+,+,-,-,+).
trans_and_write_one_procedure(end_of_file,end_of_file,OI,SN,SN,CL,CL):- !,
    optimize_flush(OI,WInstr),
    write_instr(WInstr).
trans_and_write_one_procedure(procedure(ProN,Ar),procedure(ProN,Ar),OI,SN,SN,CL,CL):- !,
    optimize_flush(OI,WInstr),
    write_instr(WInstr).
trans_and_write_one_procedure(Instr,NextProc,OI,SN,NSN,CL,CLT):-
    trans_instr(Instr,Instr2,SN,SN1,CL,CL1),
    optimize(Instr2,OI,WInstr,OO),
    write_instr(WInstr),
    read(NextInstr), !,
    trans_and_write_one_procedure(NextInstr,NextProc,OO,SN1,NSN,CL1,CLT).

:- mode trans_instr(+,-,+,-,-,+).
trans_instr(label(Lab0),label(Lab),SN,SN,CL,CL):- !,
    make_label(Lab0,Lab).
trans_instr(put_structured_constant(Const,Xj),
	    put_structured_constant(Xj,Lab),SN,NSN,[(Const,Lab)|CLT],CLT):- !,
	make_label1('$SCNST'/SN,Lab), NSN is SN + 1.
trans_instr(Instr,OPArgs,SN,SN,CL,CL):-
    tbl(Instr,OPArgs), !.

:- mode make_label(+, -).
make_label(P/A/C, Label) :-
   "_"=[Derimit],
   make_label(P/A/C, [], Name, Derimit),
   name(Label, Name).
make_label(P/A, Label) :-
   "_"=[Derimit],
   make_label(P/A/0, [], Name, Derimit),
   name(Label, Name).

:- mode make_label1(+, -).
make_label1(X, Label) :-
   "_"=[Derimit],
   make_label(X, [], Name, Derimit),
   name(Label, Name).

:- mode make_label(+, +, -, +).
make_label(L/X, Stack, Label, Derimit) :- !,
    name(X, Xn), 
  ( Stack==[], !, XL=Xn ;
    append(Xn, [Derimit|Stack], XL) ),
    make_label(L, XL, Label, Derimit).
make_label(X, Stack, Label, Derimit) :-
    name(X, Xn), append(Xn, [Derimit|Stack], Label).

:- mode append(+,+,-).
append([H|T],B,[H|C]):- !, append(T,B,C).
append([],B,B).

:- mode write_instr(+).
write_instr([]):- !.
write_instr([H|L]):- !, write_instr(H), write_instr(L).
write_instr(label(Lab)):- !,
    writeq(Lab), put(":"), nl.
write_instr(Instr):- !,
    Instr =.. [OP|Args],
    put(9), write(OP),
    write_args(Args), nl, !.

:-mode write_args(+).
write_args([]):- !.
write_args(['|'|RArg]):- put(9), put(9), put("'"), put("|"), put("'"),
	write_args1(RArg).
write_args(['!'|RArg]):- put(9), put(9), put("'"), put("!"), put("'"),
	write_args1(RArg).
write_args([Arg|RArg]):- put(9), put(9), writeq(Arg), write_args1(RArg).

:-mode write_args1(+).
write_args1([]):- !.
write_args1(['|'|RArg]):- put(","), put("'"), put("|"), put("'"),
	write_args1(RArg).
write_args1(['!'|RArg]):- put(","), put("'"), put("!"), put("'"),
	write_args1(RArg).
write_args1([Arg|RArg]):- put(","), writeq(Arg), write_args1(RArg).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%  Translate Table for PDSS                          %%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
:- mode tbl(+,-).

%%%% Control instructions %%%%
% tbl(true,			true):- !.
% tbl(fail,			fail):- !.
% tbl(jump(Lab0),		jump(Lab)):- make_lable(Lab0,Lab), !.
tbl(try_me_else(Lab0),		try_me_else(Lab)):- make_label(Lab0,Lab), !.
tbl(otherwise(Lab0),		otherwise(Lab)):- make_label(Lab0,Lab), !.
tbl(read_eagerly(Lab0),		[]):- !.	% NOT SUPPORTED !!
tbl(suspend(Lab0),		suspend(Lab)):- make_label(Lab0,Lab), !.
% tbl(proceed,			proceed):- !.
tbl(execute(PN/Na),		execute(Na,Lab)):- make_label(PN/Na,Lab), !.
tbl(execute_ext(PN/Na,Mod),	execute_external(Mod,PN,Na)):- !.
tbl(create_goal(PN/Na),		create_goal(Na)):- !.
tbl(create_with_priority(PN/Na,Xi),	create_goal(Na)):- !.
tbl(create_ext(PN/Na,Mod),	create_goal(Na)):- !.
tbl(create_ext_with_priority(PN/Na,Mod,Xi),	[]):- !.
tbl(create_to_processor(PN/Na,Proc),	create_goal(Na)):- !.
tbl(create_to_node(PN/Na,Proc),	create_goal(Na)):- !.
tbl(create_with_priority_to_processor(PN/Na,Xi,Proc),	create_goal(Na)):- !.
tbl(create_with_priority_to_node(PN/Na,Xi,Proc),	create_goal(Na)):- !.
tbl(enqueue_goal(PN/Na),	enqueue_goal(Na,Lab)):-
	make_label(PN/Na,Lab), !.
tbl(enqueue_to_processor(PN/Na,Proc), enqueue_goal(Na,Lab)):-
	make_label(PN/Na,Lab), !.
tbl(enqueue_to_node(PN/Na,Proc), enqueue_goal(Na,Lab)):-
	make_label(PN/Na,Lab), !.
tbl(enqueue_with_priority(PN/Na,Xi), enqueue_goal_with_priority(Na,Lab,Xi)):-
	make_label(PN/Na,Lab), !.
tbl(enqueue_with_priority_to_processor(PN/Na,Xi,Proc),
	enqueue_goal_with_priority(Na,Lab,Xi)):- make_label(PN/Na,Lab), !.
tbl(enqueue_with_priority_to_node(PN/Na,Xi,Proc),
	enqueue_goal_with_priority(Na,Lab,Xi)):- make_label(PN/Na,Lab), !.
tbl(enqueue_ext(PN/Na,Mod),	enqueue_goal_external(Mod,PN,Na)):- !.
tbl(enqueue_ext_with_priority(PN/Na,Xi,Mod),
	enqueue_goal_external_with_priority(Mod,PN,Na,Xi)):- !.

%%%% Passive unification instructions %%%%
tbl(wait(Xi,_),			wait(Xi)):- !.

tbl(is_atom(Xi,Lab0),		is_atom(Xi,Lab)):- make_label(Lab0,Lab), !.
tbl(is_integer(Xi,Lab0),	is_integer(Xi,Lab)):- make_label(Lab0,Lab), !.
tbl(is_float(Xi,Lab0),		is_float(Xi,Lab)):- make_label(Lab0,Lab), !.
tbl(is_vector(Xi,Lab0),		is_vector(Xi,Lab)):- make_label(Lab0,Lab), !.
tbl(is_string(Xi,Lab0),		is_string(Xi,Lab)):- make_label(Lab0,Lab), !.
tbl(switch_on_type(Xi,La0,Li0,Ll0,Lv0,Ls0,Lf0),
	switch_on_type(Xi,La,Li,Ll,Lv,Ls,Lf)):-
	make_label(La0,La), make_label(Li0,Li), make_label(Ll0,Ll),
	make_label(Lv0,Lv), make_label(Ls0,Ls), make_label(Lf0,Lf), !.

tbl(test_constant([],Xi,Lab0),	test_nil(Xi,Lab)):-
	make_label(Lab0,Lab), !.
tbl(test_constant(C,Xi,Lab0), 	test_atom(Xi,C,Lab)):- atom(C),
	make_label(Lab0,Lab), !.
tbl(test_constant(C,Xi,Lab0),	test_integer(Xi,C,Lab)):- integer(C),
	make_label(Lab0,Lab), !.
tbl(test_constant(C,Xi,Lab0),	test_float(Xi,C,Lab)):- float(C),
	make_label(Lab0,Lab), !.
tbl(test_arity(NAr,Xi,Lab0),	test_arity(Xi,NAr,Lab)):-
	make_label(Lab0,Lab), !.
tbl(branch_on_constant(Xi,LL), Instrs):-
	split_fail(LL,LL1,L0), make_label(L0,L),
	gen_indx_instrs(Xi,LL1,Instrs,L), !.
tbl(branch_on_arity(Xi,LL),	[jump_on_arity(Xi,Size,L)|Instrs]):-
	split_fail(LL,LL1,L0),
	max(LL1,0,Size1), Size is Size1+1, make_label(L0,L),
	gen_densely_table_entrys(LL1,0,N,Instrs,[],L), !.

tbl(atom(Xi,_),			atom(Xi)):- !.
tbl(integer(Xi,_),		integer(Xi)):- !.
tbl(float(Xi,_),		float(Xi)):- !.
tbl(wait_list(Xi,_),		list(Xi)):- !.
tbl(vector(Xi,Xj),		g_vector(Xi,Xj)):- integer(Xj), !.
tbl(vector(Xi,_),		vector(Xi)):- !.
tbl(deref_vector(Xi,_),		vector(Xi)):- !.
tbl(string(Xi,_),		string(Xi)):- !.
tbl(wait_string(Xi,_),		string(Xi)):- !.

tbl(jump_on_non_atom(Xi,Lab0),	jump_on_non_atom(Xi,Lab)):-
	make_label(Lab0,Lab), !.
tbl(jump_on_non_integer(Xi,Lab0), jump_on_non_integer(Xi,Lab)):-
	make_label(Lab0,Lab), !.
tbl(jump_on_non_float(Xi,Lab0), jump_on_non_float(Xi,Lab)):-
	make_label(Lab0,Lab), !.
tbl(jump_on_non_list(Xi,Lab0),	jump_on_non_list(Xi,Lab)):-
	make_label(Lab0,Lab), !.
tbl(jump_on_non_vector(Xi,Lab0), jump_on_non_vector(Xi,Lab)):-
	make_label(Lab0,Lab), !.
tbl(jump_on_non_string(Xi,Lab0), jump_on_non_string(Xi,Lab)):-
	make_label(Lab0,Lab), !.

tbl(check_constant([],Xi,Lab0),	check_nil(Xi,Lab)):-
	make_label(Lab0,Lab), !.
tbl(check_constant(C,Xi,Lab0),	check_atom(Xi,C,Lab)):- atom(C),
	make_label(Lab0,Lab), !.
tbl(check_constant(C,Xi,Lab0),	check_integer(Xi,C,Lab)):- integer(C),
	make_label(Lab0,Lab), !.
tbl(check_constant(C,Xi,Lab0),	check_float(Xi,C,Lab)):- float(C),
	make_label(Lab0,Lab), !.
tbl(check_vector(NAr,Xi,Lab0),	check_vector(Xi,NAr,Lab)):-
	make_label(Lab0,Lab), !.

tbl(wait_constant([],Xi,_),	wait_nil(Xi)):- !.
tbl(wait_constant(C,Xi,_),	wait_atom(Xi,C)):- atom(C), !.
tbl(wait_constant(C,Xi,_),	wait_integer(Xi,C)):- integer(C), !.
tbl(wait_constant(C,Xi,_),	wait_float(Xi,C)):- float(C), !.
tbl(wait_vector(Xi,NAr,_),	wait_vector(Xi,NAr)):- !.

tbl(wait_value(Xi,Xj,_),	wait_value(Xi,Xj)):- !.

%%%% Read element of structure instructions %%%%
% tbl(read_car(Xl,Xi),		read_car(Xl,Xi)):- !.
% tbl(read_cdr(Xl,Xi),		read_cdr(Xl,Xi)):- !.
% tbl(read_element(Xv,Idx,Xi),	read_element(Xv,Idx,Xi)):- !.

%%%% Put, set & write value instructions %%%%
tbl(put_value(0,Xj),		[]):- !.
tbl(put_value(Xi,0),		[]):- !.
tbl(put_value(Xs,Xd),		put_value(Xd,Xs)):- !.
tbl(put_marked_value(Xs,Xd),	put_marked_value(Xd,Xs)):- !.

tbl(set_value(Xi,Gi),		set_value(Gi,Xi)):- !.
tbl(set_marked_value(Xi,Gi),	set_marked_value(Gi,Xi)):- !.

% tbl(write_car_value(Xl,Xi),	write_car_value(Xl,Xi)):- !.
% tbl(write_cdr_value(Xl,Xi),	write_cdr_value(Xl,Xi)):- !.
% tbl(write_element_value(Xv,Idx,Xi),	wirte_element_value(Xv,Idx,Xi)):- !.
% tbl(write_car_marked_value(Xl,Xi),	write_car_marked_value(Xl,Xi)):- !.
% tbl(write_cdr_marked_value(Xl,Xi),	write_cdr_marked_value(Xl,Xi)):- !.
% tbl(write_element_marked_value(Xv,Idx,Xi),
% 	wirte_element_marked_value(Xv,Idx,Xi)):- !.

%%%% Put, set & write constant instructions %%%%
tbl(put_constant(_,0),		[]):- !.
tbl(put_constant([],Xi),	put_nil(Xi)):- !.
tbl(put_constant(C,Xi),		put_atom(Xi,C)):- atom(C), !.
tbl(put_constant(C,Xi),		put_integer(Xi,C)):- integer(C), !.
tbl(put_constant(C,Xi),		put_float(Xi,C)):- float(C), !.
% tbl(put_list(Xi),		put_list(Xi)):- !.
tbl(put_reused_list(Xl,Xi),	put_reused_list(Xi,Xl)):- !.
% tbl(put_vector(Xi,NAr),	put_vector(Xi,NAr)):- !.
tbl(put_reused_vector(Xv,Xi,NAr),  put_reused_vector(Xi,Xv)):- !.
tbl(put_structured_constant(Xi,Lab0),	put_structured_constant(Xi,Lab)):-
	make_label1(Lab0,Lab), !.

tbl(set_constant([],Gi),	set_nil(Gi)):- !.
tbl(set_constant(C,Gi),		set_atom(Gi,C)):- atom(C), !.
tbl(set_constant(C,Gi),		set_integer(Gi,C)):- integer(C), !.
tbl(set_constant(C,Gi),		set_float(Gi,C)):- float(C), !.

tbl(write_car_constant(Xl,[]),	write_car_nil(Xl)):- !.
tbl(write_cdr_constant(Xl,[]),	write_cdr_nil(Xl)):- !.
tbl(write_element_constant(Xv,Idx,[]), write_element_nil(Xv,Idx)):- !.
tbl(write_car_constant(Xl,C),	write_car_atom(Xl,C)):- atom(C), !.
tbl(write_cdr_constant(Xl,C),	write_cdr_atom(Xl,C)):- atom(C), !.
tbl(write_element_constant(Xv,Idx,C), write_element_atom(Xv,Idx,C)):-
	atom(C), !.
tbl(write_car_constant(Xl,C),	write_car_integer(Xl,C)):- integer(C), !.
tbl(write_cdr_constant(Xl,C),	write_cdr_integer(Xl,C)):- integer(C), !.
tbl(write_element_constant(Xv,Idx,C), write_element_integer(Xv,Idx,C)):-
	integer(C), !.
tbl(write_car_constant(Xl,C),	write_car_float(Xl,C)):- float(C), !.
tbl(write_cdr_constant(Xl,C),	write_cdr_float(Xl,C)):- float(C), !.
tbl(write_element_constant(Xv,Idx,C), write_element_float(Xv,Idx,C)):-
	float(C), !.

%%%% Put, set & write variable instructions %%%%
tbl(put_variable(0,0),		[]):- !.
tbl(put_variable(Xi,0),		put_void(Xi)):- !.
tbl(put_variable(0,Xj),		put_void(Xj)):- !.
% tbl(put_variable(Xi,Xj),	put_variable(Xi,Xj)):- !.
% tbl(put_marked_variable(Xi,Xj),	put_marked_variable(Xi,Xj)):- !.

tbl(set_variable(0,0),		[]):- !.
tbl(set_variable(0,Gi),		set_void(Gi)):- !.
tbl(set_variable(Xi,0),		put_void(Xi)):- !. % ???
tbl(set_variable(Xi,Gi),	set_variable(Gi,Xi)):- !.
tbl(set_marked_variable(Xi,Gi),	set_marked_variable(Gi,Xi)):- !.

tbl(write_car_variable(Xl,0),	write_car_void(Xl)):- !.
tbl(write_cdr_variable(Xl,0),	write_cdr_void(Xl)):- !.
tbl(write_element_variable(Xv,Idx,0),	write_element_void(Xv,Idx)):- !.
% tbl(write_car_variable(Xl,Xi),	write_car_variable(Xl,Xi)):- !.
% tbl(write_cdr_variable(Xl,Xi),	write_cdr_variable(Xl,Xi)):- !.
% tbl(write_element_variable(Xv,Idx,Xi),write_element_variable(Xv,Idx,Xi)):- !.
% tbl(write_car_marked_variable(Xl,Xi),	write_car_marked_variable(Xl,Xi)):- !.
% tbl(write_cdr_marked_variable(Xl,Xi),	write_cdr_marked_variable(Xl,Xi)):- !.
% tbl(write_element_marked_variable(Xv,Idx,Xi),
%	write_element_marked_variable(Xv,Idx,Xi)):- !.

%%%% Active unification instructions %%%%
tbl(get_constant([],Xi),	get_nil(Xi)):- !.
tbl(get_constant(C,Xi),		get_atom(Xi,C)):- atom(C), !.
tbl(get_constant(C,Xi),		get_integer(Xi,C)):- integer(C), !.
tbl(get_constant(C,Xi),		get_float(Xi,C)):- float(C), !.
tbl(get_list_value(Xl,Xi),	get_list_value(Xi,Xl)):- !.
tbl(get_vector_value(Xv,Xi),	get_vector_value(Xi,Xv)):- !.
% tbl(get_value(Xv,Xi),		get_value(Xi,Xv)):- !.

%%%% MRB GC instructions %%%%
tbl(collect_value(Xi),		collect_value(Xi)):- deb, !.
tbl(collect_value(Xi),		[]):- !.
tbl(collect_list(Xl),		collect_list(Xl)):- deb, !.
tbl(collect_list(Xl),		[]):- !.
tbl(collect_vector(Xv,N),	collect_vector(Xv)):- deb, !.
tbl(collect_vector(Xv,N),	[]):- !.

%%%% Guard builtin predicate instructions %%%%
tbl(diff(X1,X2,_),	 	g_diff(X1,X2)):- !.

tbl(equal(X1,X2,_),		g_equal(X1,X2)):- !.
tbl(not_equal(X1,X2,_),		g_not_equal(X1,X2)):- !.
tbl(less_than(X1,X2,_),		g_less_than(X1,X2)):- !.
tbl(not_less_than(X1,X2,_),	g_not_less_than(X1,X2)):- !.

tbl(add(X1,X2,X3),		g_add(X1,X2,X3)):- !.
tbl(subtract(X1,X2,X3),		g_subtract(X1,X2,X3)):- !.
tbl(multiply(X1,X2,X3),		g_multiply(X1,X2,X3)):- !.
tbl(divide(X1,X2,X3),		g_divide(X1,X2,X3)):- !.
tbl(modulo(X1,X2,X3),		g_modulo(X1,X2,X3)):- !.
tbl(minus(X1,X2),		g_minus(X1,X2)):- !.
tbl(abs(X1,X2),			g_abs(X1,X2)):- !.
tbl(min(X1,X2,X3),		g_min(X1,X2,X3)):- !.
tbl(max(X1,X2,X3),		g_max(X1,X2,X3)):- !.
tbl(and(X1,X2,X3),		g_and(X1,X2,X3)):- !.
tbl(or(X1,X2,X3),		g_or(X1,X2,X3)):- !.
tbl(exclusive_or(X1,X2,X3),	g_exclusive_or(X1,X2,X3)):- !.
tbl(complement(X1,X2),		g_complement(X1,X2)):- !.
tbl(increment(X1,X2),		g_increment(X1,X2)):- !.
tbl(decrement(X1,X2),		g_decrement(X1,X2)):- !.
tbl(abs(X1,X2),			g_abs(X1,X2)):- !.
tbl(min(X1,X2,X3),		g_min(X1,X2,X3)):- !.
tbl(max(X1,X2,X3),		g_max(X1,X2,X3)):- !.
tbl(shift_left(X1,X2,X3),	g_shift_left(X1,X2,X3)):- !.
tbl(shift_right(X1,X2,X3),	g_shift_right(X1,X2,X3)):- !.

tbl(vector(X1,X2),		g_vector(X1,X2)):- !.
tbl(vector_element(X1,X2,X3),	g_vector_element(X1,X2,X3)):- !.
% tbl(mark_element(X1,X2),	mark_element(X1,X2)):- !.

tbl(string(X1,X2,X3),		g_string(X1,X2,X3)):- !.
tbl(string_element(X1,X2,X3),	g_string_element(X1,X2,X3)):- !.

%%%% Body builtin predicate instructions %%%%
%%%% (.klb and .asm instructions have same name and arguments) %%%%

%%%% Console I/O builtin predicate instructions %%%%
% tbl(display_console(X1),	display_console(X1)):- !.
% tbl(put_console(X1),		put_console(X1)):- !.
% tbl(read_console(X1),		read_console(X1)):- !.

%%%% Guard builtin predicate instructions (float) %%%%
tbl(floating_point_equal(X1,X2,_),	g_float_equal(X1,X2)):- !.
tbl(floating_point_not_equal(X1,X2,_),	g_float_not_equal(X1,X2)):- !.
tbl(floating_point_less_than(X1,X2,_),	g_float_less_than(X1,X2)):- !.
tbl(floating_point_not_less_than(X1,X2,_), g_float_not_less_than(X1,X2)):- !.

tbl(floating_point_add(X1,X2,X3),	g_float_add(X1,X2,X3)):- !.
tbl(floating_point_subtract(X1,X2,X3),	g_float_subtract(X1,X2,X3)):- !.
tbl(floating_point_multiply(X1,X2,X3),	g_float_multiply(X1,X2,X3)):- !.
tbl(floating_point_divide(X1,X2,X3),	g_float_divide(X1,X2,X3)):- !.
tbl(floating_point_minus(X1,X2),	g_float_minus(X1,X2)):- !.
tbl(floating_point_abs(X1,X2),		g_float_abs(X1,X2)):- !.
tbl(floating_point_min(X1,X2,X3),	g_float_min(X1,X2,X3)):- !.
tbl(floating_point_max(X1,X2,X3),	g_float_max(X1,X2,X3)):- !.
tbl(floating_point_floor(X1,X2),	g_float_floor(X1,X2)):- !.
tbl(floating_point_sqrt(X1,X2),		g_float_sqrt(X1,X2)):- !.
tbl(floating_point_ln(X1,X2),		g_float_ln(X1,X2)):- !.
tbl(floating_point_log(X1,X2),		g_float_log(X1,X2)):- !.
tbl(floating_point_exp(X1,X2),		g_float_exp(X1,X2)):- !.
tbl(floating_point_pow(X1,X2,X3),	g_float_pow(X1,X2,X3)):- !.
tbl(floating_point_sin(X1,X2),		g_float_sin(X1,X2)):- !.
tbl(floating_point_cos(X1,X2),		g_float_cos(X1,X2)):- !.
tbl(floating_point_tan(X1,X2),		g_float_tan(X1,X2)):- !.
tbl(floating_point_asin(X1,X2),		g_float_asin(X1,X2)):- !.
tbl(floating_point_acos(X1,X2),		g_float_acos(X1,X2)):- !.
tbl(floating_point_atan(X1,X2),		g_float_atan(X1,X2)):- !.
tbl(floating_point_atan(X1,X2,X3),	g_float_atan2(X1,X2,X3)):- !.
tbl(floating_point_sinh(X1,X2),		g_float_sinh(X1,X2)):- !.
tbl(floating_point_cosh(X1,X2),		g_float_cosh(X1,X2)):- !.
tbl(floating_point_tanh(X1,X2),		g_float_tanh(X1,X2)):- !.

tbl(floating_point_to_integer(X1,X2),	g_float_to_integer(X1,X2)):- !.
tbl(integer_to_floating_point(X1,X2),	g_integer_to_float(X1,X2)):- !.

%%%% Body builtin predicate instructions (float) %%%%
%%%% (.klb and .asm instructions have same name and arguments) %%%%

%%%% Body builtin predicate instructions (system) %%%%
%%%% (.klb and .asm instructions have same name and arguments) %%%%

%%%% Guard builtin predicate instructions (system) %%%%
% tbl(statistics(X1,X2,X3,X4,X5,X6),	statistics(X1,X2,X3,X4,X5,X6)):- !.
% tbl(get_cpu_time(X1),			get_cpu_time(X1)):- !.
% tbl(get_current_time(X1,X2,X3,X4,X5,X6),
%	get_current_time(X1,X2,X3,X4,X5,X6)):- !.
tbl(halt(X1),				g_halt(X1)):- !.
tbl(request_gc(X1),			g_request_gc(X1)):- !.
tbl(set_scheduling_switch(X1),		g_set_scheduling_switch(X1)):- !.
tbl(set_trace_switch(X1),		g_set_trace_switch(X1)):- !.
tbl(set_backtrace_switch(X1),		g_set_backtrace_switch(X1)):- !.
tbl(device_dup_check(X1),		g_device_dup_check(X1)):- !.

%% Firm Test
tbl(tag_and_value(X1,X2,X3),		g_tag_and_value(X1,X2,X3)):- !.
tbl(register_tag_and_value(X1,X2,X3),  g_register_tag_and_value(X1,X2,X3)):- !.
tbl(word(X1,X2,X3),			g_word(X1,X2,X3)):- !.
tbl(set_tag_and_value(X1,X2,X3),	g_set_tag_and_value(X1,X2,X3)):- !.

%%%% Other instructions %%%%
tbl(X,X).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
gen_indx_instrs(Ai, LL, [Instr0|Instrs], L) :- LL=[(Cnst,_)|_], atom(Cnst), !,
  ( less_than(LL, 4), Instr0 = branch_on_atom(Ai, Size, L) ;
    Instr0 = hash_on_atom(Ai, Size, L) ), !,
    gen_table_entrys(LL, Instrs, 0, Size).
gen_indx_instrs(Ai, LL, [Instr0|Instrs], L) :-  /* integer */
    less_than(LL, 4), !,
  ( densely(LL, Size), !, Instr0=jump_on_integer(Ai,Size1,L), Size1 is Size+1,
        gen_densely_table_entrys(LL, 0, N, Instrs, [], L) ;
    Instr0=branch_on_integer(Ai,Size,L),
        gen_table_entrys(LL, Instrs, 0, Size) ).
gen_indx_instrs(Ai, LL, [Instr0|Instrs], L) :-  /* integer */
  ( densely(LL, Size), !, Instr0=jump_on_integer(Ai,Size1,L), Size1 is Size+1,
        gen_densely_table_entrys(LL, 0, N, Instrs, [], L) ;
    Instr0=hash_on_integer(Ai,Size,L),
        gen_table_entrys(LL, Instrs, 0, Size) ).

gen_table_entrys([(Cnst,Lab0)|LL], [Instr|Instrs], K, N) :-
    gen_table_entry(Cnst,Lab0, Instr),
    K1 is K+1,
    gen_table_entrys(LL, Instrs, K1, N).
gen_table_entrys([], [], N, N) :- !.

gen_table_entry(Cnst,Lab0, Instr) :- atom(Cnst), !,
    Instr=bucket_entry_a(Cnst, Lab), make_label(Lab0, Lab).
gen_table_entry(Cnst,Lab0, Instr) :- integer(Cnst),
    Instr=bucket_entry_i(Cnst, Lab), make_label(Lab0, Lab).

gen_densely_table_entrys([(K,Lab0)|LL],K,N,[table_entry(Lab)|Is],It,L) :- !,
    make_label(Lab0, Lab),
    K1 is K+1,
    gen_densely_table_entrys(LL, K1, N, Is, It, L).
gen_densely_table_entrys([E|LL], K, N, [table_entry(L)|Is], It, L) :- !,
    K1 is K+1,
    gen_densely_table_entrys([E|LL], K1, N, Is, It, L).
gen_densely_table_entrys([], N, N, Is, Is, _).

gen_densely_table_dummy(N, N, [], _) :- !.
gen_densely_table_dummy(K, Size, [table_entry(L)|Is], L) :-
    K1 is K+1,
    gen_densely_table_dummy(K1, Size, Is, L).

densely([(I,_)|_], TableSize) :- I<0, !, fail.
densely(LL, TableSize) :-
    check_densely(LL, _, 0, Max),
    jump_table_size(Max, TableSize).

check_densely([(I,_)|LL], _, En, Max) :-
    En1 is En+1,
    densely_1(En, I), !, check_densely(LL, I, En1, Max).
check_densely([], Max, _, Max).

densely_1(ElementNumber, CurrentMax) :-
    ElementNumber =< 32, !,
    (CurrentMax - ElementNumber) =< 24.
densely_1(ElementNumber, CurrentMax) :-
   ElementNumber < 128, !,
   (CurrentMax - ElementNumber) =< 64.
densely_1(ElementNumber, CurrentMax) :-
   (CurrentMax / ElementNumber) < 2.

jump_table_size(I, I).

less_than([], L) :- L>0, !.
less_than([_|Cdr], L) :- L=:=0, !, fail.
less_than([_|Cdr], L) :- L1 is L-1, less_than(Cdr, L1).

max([(I,_)|LL], _, Max) :- !, max(LL, I, Max).
max([], Max, Max) :- !.

len([_|T], L, Len) :- !, L1 is L+1, len(T, L1, Len).
len([], Len, Len).

split_fail([Fail], [], Fail) :- !.
split_fail([X|T], [X|L], Fail) :- split_fail(T, L, Fail).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
:- mode optimize(+,+,-,-).

% for BUG of Compiler.
optimize(put_int(0,P),[put_atom(R,'*')|X],W,O):- !,
	optimize_flush([b_rate(R,R),put_int(R,P)|X],W), O=[].
optimize(put_int(0,P),[put_atom(R,'$')|X],W,O):- !,
	optimize_flush([b_rltv(R,R),put_int(R,P)|X],W), O=[].

optimize(read_cdr(R,T),[read_car(R,H),list(R)|X],W,O):- !,
	optimize_flush([wait_list_var_var(R,H,T)|X],W), O=[].
optimize(read_cdr(R,T),[read_car(R,H),jump_on_non_list(R,Lab)|X],W,O):- !,
	optimize_flush([jump_on_non_list_var_var(R,Lab,H,T)|X],W), O=[].

optimize(write_element_atom(R,0,A),[put_vector(R,N)|X],W,O):- !,
	optimize_flush([put_func(R,N,A)|X],W), O=[].
optimize(write_element_atom(R,0,A),[put_reused_vector(R,V)|X],W,O):- !,
	optimize_flush([put_reused_func(R,V,A)|X],W), O=[].

optimize(write_cdr_value(R,T),[write_car_value(R,H),put_list(R)|X],W,O):- !,
	optimize_flush([put_list_val_val(R,H,T)|X],W), O=[].
optimize(write_cdr_value(R,T),
	[write_car_value(R,H),put_reused_list(R,L)|X],W,O):- !,
	optimize_flush([put_reused_list_val_val(R,L,H,T)|X],W), O=[].

optimize(get_list_value(U,R),
	 [write_cdr_variable(R,T),write_car_value(R,H),put_list(R)|X],W,O):- !,
	optimize_flush([get_list_val_var(U,R,H,T)|X],W), O=[].
optimize(get_list_value(U,R),
	 [write_cdr_variable(R,T),write_car_value(R,H),put_reused_list(R,L)|X],
	 W,O):- !,
	optimize_flush([get_reused_list_val_var(U,R,L,H,T)|X],W), O=[].

optimize(I,
	[write_cdr_variable(R,T),write_car_value(R,H),put_list(R)|X],W,O):- !,
	optimize_flush([put_list_val_var(R,H,T)|X],W), O=[I].
optimize(I,
	[write_cdr_variable(R,T),write_car_value(R,H),put_reused_list(R,L)|X],
	W,O):- !,
	optimize_flush([put_reused_list_val_var(R,L,H,T)|X],W), O=[I].

optimize(read_element(V,I,R),[read_element(V,I0,R0)|X],W,O):-
	R is R0+1, I is I0+1, !,
	optimize_flush(X,W), O=[read_elements_inc(V,I0,R0,2)].
optimize(read_element(V,I,R),[read_element(V,I0,R0)|X],W,O):-
	R is R0-1, I is I0+1, !,
	optimize_flush(X,W), O=[read_elements_dec(V,I0,R0,2)].
optimize(read_element(V,I,R),[read_elements_inc(V,I0,R0,N)|X],W,O):-
	R is R0+N, I is I0+N, !,
	optimize_flush(X,W), O=[read_elements_inc(V,I0,R0,NN)], NN is N+1.
optimize(read_element(V,I,R),[read_elements_dec(V,I0,R0,N)|X],W,O):-
	R is R0-N, I is I0+N, !,
	optimize_flush(X,W), O=[read_elements_dec(V,I0,R0,NN)], NN is N+1.

optimize(write_element_value(V,I,R),[write_element_value(V,I0,R0)|X],W,O):-
	R is R0+1, I is I0+1, !,
	optimize_flush(X,W), O=[write_elements_inc(V,I0,R0,2)].
optimize(write_element_value(V,I,R),[write_element_value(V,I0,R0)|X],W,O):-
	R is R0-1, I is I0+1, !,
	optimize_flush(X,W), O=[write_elements_dec(V,I0,R0,2)].
optimize(write_element_value(V,I,R),[write_elements_inc(V,I0,R0,N)|X],W,O):-
	R is R0+N, I is I0+N, !,
	optimize_flush(X,W), O=[write_elements_inc(V,I0,R0,NN)], NN is N+1.
optimize(write_element_value(V,I,R),[write_elements_dec(V,I0,R0,N)|X],W,O):-
	R is R0-N, I is I0+N, !,
	optimize_flush(X,W), O=[write_elements_dec(V,I0,R0,NN)], NN is N+1.

optimize(put_value(D,R),[put_value(D0,R0)|X],W,O):-
	R is R0+1, D is D0+1, !,
	optimize_flush(X,W), O=[put_values_inc(D0,R0,2)].
optimize(put_value(D,R),[put_value(D0,R0)|X],W,O):-
	R is R0-1, D is D0+1, !,
	optimize_flush(X,W), O=[put_values_dec(D0,R0,2)].
optimize(put_value(D,R),[put_values_inc(D0,R0,N)|X],W,O):-
	R is R0+N, D is D0+N, !,
	optimize_flush(X,W), O=[put_values_inc(D0,R0,NN)], NN is N+1.
optimize(put_value(D,R),[put_values_dec(D0,R0,N)|X],W,O):-
	R is R0-N, D is D0+N, !,
	optimize_flush(X,W), O=[put_values_dec(D0,R0,NN)], NN is N+1.

optimize(set_value(A,R),[set_value(A0,R0)|X],W,O):-
	R is R0+1, A is A0+1, !,
	optimize_flush(X,W), O=[set_values_inc(A0,R0,2)].
optimize(set_value(A,R),[set_value(A0,R0)|X],W,O):-
	R is R0-1, A is A0+1, !,
	optimize_flush(X,W), O=[set_values_dec(A0,R0,2)].
optimize(set_value(A,R),[set_values_inc(A0,R0,N)|X],W,O):-
	R is R0+N, A is A0+N, !,
	optimize_flush(X,W), O=[set_values_inc(A0,R0,NN)], NN is N+1.
optimize(set_value(A,R),[set_values_dec(A0,R0,N)|X],W,O):-
	R is R0-N, A is A0+N, !,
	optimize_flush(X,W), O=[set_values_dec(A0,R0,NN)], NN is N+1.

optimize([H|L],I,W,[]):- !, optimize_flush(I,W,[H|L]).
optimize([],I,W,[]):- !, optimize_flush(I,W,[]).

optimize(X,I,[],[X|I]).


:- mode optimize_flush(+,-).
optimize_flush(O,W):- optimize_flush(O,W,[]).

:- mode optimize_flush(+,-,+).
optimize_flush([H|O],W,L):- optimize_flush(O,W,[H|L]).
optimize_flush([],W,L):- W=L.


:- mode optimize_flush(+,-).
optimize_flush(O,W):- optimize_flush(O,W,[]).

:- mode optimize_flush(+,-,+).
optimize_flush([H|O],W,L):- optimize_flush(O,W,[H|L]).
optimize_flush([],W,L):- W=L.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- mode write_constant_section(+,+).
write_constant_section(_,[]):- !.
write_constant_section(MName,ConstList):- !,
	compress_structured_constant(ConstList,[],CL),
	trans_structured_constant(CL,InstrList),
	write_instr([begin_const_section(MName)|InstrList]).

:- mode compress_structured_constant(+,+,-).
compress_structured_constant([(Const,Lab)|ConstList],L,CL):- !,
	compress_one_struct_const(Const,Lab,L,LL),
	compress_structured_constant(ConstList,LL,CL).
compress_structured_constant([],CL,CL):- !.

:- mode compress_one_struct_const(+,+,+,-).
compress_one_struct_const(Const,Lab,[],CL):- !,
	CL = [(Const,[Lab])].
compress_one_struct_const(Const,Lab,[(Const,LabL)|L],CL):- !,
	CL = [(Const,[Lab|LabL])|L].
compress_one_struct_const(Const,Lab,[H|T],CL):- !,
	CL = [H|CLT],
	compress_one_struct_const(Const,Lab,T,CLT).

:- mode trans_structured_constant(+,-).
trans_structured_constant([(Const,LabL)|CL],IL):- !,
	labels(LabL,Lab,ILT,ILT1),
	trans_one_struct_const(Const,Lab,0,_,Instr,IL,ILT),
	ILT1 = [Instr|ILL],
	trans_structured_constant(CL,ILL).
trans_structured_constant([],[]):- !.

:- mode labels(+,-,-,+).
labels([Lab],Lab,[label(Lab)|IL],IL):- !.
labels([Lab|LL],Lab0,[label(Lab)|ILT],IL):- !,
	labels(LL,Lab0,ILT,IL).

:- mode trans_one_struct_const(+,+,+,-,-,-,+).
trans_one_struct_const(Cnst,_,N,N,Instr,IL,IL):- atom(Cnst), !,
	Instr = define_atom(Cnst).
trans_one_struct_const(Cnst,_,N,N,Instr,IL,IL):- integer(Cnst), !,
	Instr = define_integer(Cnst).
trans_one_struct_const(Cnst,_,N,N,Instr,IL,IL):- float(Cnst), !,
	Instr = define_float(Cnst).
trans_one_struct_const('$SCNST'('$VECT'(Size),Vector),Lab,N,M,Instr,IH,IT):-
	Vector =.. ['$VECT'|EList], !,
	NN is N + 1,
	trans_struct_const_element(EList,Lab,NN,M,IL,IT,IH,EIL),
	make_label1(Lab/N,Lab1),
	Instr = define_vector(Lab1),
	Length is Size/\8'77777777,
	EIL = [label(Lab1),define_desc(0,Length)|IL].
trans_one_struct_const('$SCNST'('$LIST'(2),List),Lab,N,M,Instr,IH,IT):-
	List =.. ['$LIST'|EList], !,
	NN is N + 1,
	trans_struct_const_element(EList,Lab,NN,M,IL,IT,IH,EIL),
	make_label1(Lab/N,Lab1),
	Instr = define_list(Lab1),
	EIL = [label(Lab1)|IL].
trans_one_struct_const('$SCNST'(string,CharList),Lab,N,M,Instr,IH,IT):- !,
	make_label1(Lab/N,Lab1),
	M is N + 1,
	Instr = define_string(Lab1),
	len(CharList,0,Len),
	Rest is 3 - ((Len+3) mod 4),
	Type is 3 \/ (Rest << 3),	%% 3 (10) = 011 (2)
	Length is (Len+3) >> 2,		%% (Len+3) / 4
	IH = [label(Lab1),define_desc(Type,Length)|IL],
	trans_string_value(CharList,IL,IT).
trans_one_struct_const('$SCNST'(ascii,CharList),Lab,N,M,Instr,IH,IT):- !,
	trans_one_struct_const('$SCNST'(string,CharList),Lab,N,M,Instr,IH,IT).

:- mode trans_struct_const_element(+,+,+,-,-,+,-,+).
trans_struct_const_element([],_,N,N,IL,IL,EIL,EIL):- !.
trans_struct_const_element([E|EL],Lab,N,M,IH,IT,EIH,EIT):- !,
	trans_one_struct_const(E,Lab,N,NN,Instr,EIH,EIL),
	IH = [Instr|IL],
	trans_struct_const_element(EL,Lab,NN,M,IL,IT,EIL,EIT).

:- mode trans_string_value(+,-,+).
trans_string_value([],IH,IT):- !,
	IH = IT.
trans_string_value(CL,IH,IT):- !,
	trans_string_value(CL,0,0,IH,IT).

:- mode trans_string_value(+,+,+,-,+).
trans_string_value([],_,Int,IH,IT):- !,
	IH = [define_integer(Int)|IT].
trans_string_value([C|CL],S,Int,IH,IT):- S<4, !,
	Int1 is Int \/ (C << (S * 8)),
	S1 is S + 1,
	trans_string_value(CL,S1,Int1,IH,IT).
trans_string_value(CL,S,Int,IH,IT):- !,
	IH = [define_integer(Int)|Instr],
	trans_string_value(CL,0,0,Instr,IT).

:- mode error(+,+).
error(Format, Args) :-
    telling(Old), tell(user),
    nl, display('** '),
    format(Format, Args),
    nl,
    tell(Old).
