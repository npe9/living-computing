%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% GUARD COMPILATION

%:- mode compile_guard(+, ?, +, -, +, +, +, -, ?).
compile_guard([], _, PC, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) --> !.
compile_guard([H|T], Fail, PC0, PC, Tabs0-Tabs, Aux0-Aux, Keep0-Keep) -->
    compile_guard_goal(H, Fail, PC0, PC1, Tabs0-Tabs1, 
                                          Aux0-Aux1, 
					  Keep0-Keep1), !,
    compile_guard(T, Fail, PC1, PC, Tabs1-Tabs, Aux1-Aux, Keep1-Keep).

%:- mode compile_guard_goal(+, ?, +, -, +, +, +, -, ?).
compile_guard_goal(V=X, Fail, PC0, PC, Tabs0-Tabs, AUX, KEEP) --> !,
  ( { newvar(V, PC0, Tabs0, Tabs1) }, !, 
	compile_get_variable(X, V, PC0, PC, Tabs1-Tabs, AUX, KEEP);
    { refvar(V, PC0, Tabs0, Tabs1) }, 
	compile_get_value(X, V, Fail, PC0, PC, Tabs1-Tabs, AUX, KEEP) ).
compile_guard_goal(read(X,Attr,M), _, PC0, PC, TABLE, AUX, KEEP) --> !,
    compile_passive_read(M, PC0, PC, TABLE, AUX, KEEP, X, Attr).
compile_guard_goal(check(X), Fail, PC0, PC, TABLE, AUX, KEEP) --> !,
    compile_passive_check(X, Fail, PC0, PC, TABLE, AUX, KEEP).
compile_guard_goal(calculate(X), _, PC0, PC, TABLE, AUX, KEEP) --> !,
    compile_passive_calculate(X, PC0, PC, TABLE, AUX, KEEP).
compile_guard_goal(branch(X), _, PC0, PC, TABLE, AUX, KEEP) --> !,
    compile_passive_branch(X, PC0, PC, TABLE, AUX, KEEP). % 890605 Nishizaki
compile_guard_goal(compare(X), Fail, PC0, PC, TABLE, AUX, KEEP) --> !,
    compile_passive_compare(X, Fail, PC0, PC, TABLE, AUX, KEEP).
compile_guard_goal(try_me_else(Fail), _, PC0, PC, T-T, A-A, _-PC0) --> !,
    gen(try_me_else(Fail), PC0, PC).	

%:- mode compile_get_variable(+, +, +, -, +, +, +, -, ?).
compile_get_variable(var(X), V, PC, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) -->
    { newvar(X, PC, Tabs, _) }, !, 
    { error('Var-var unification not implemented in guard') }.
compile_get_variable(var(X), V, PC0, PC, Tabs0-Tabs, 
                                         Aux0-Aux1, 
					 Keep-Keep) --> !,
    { refvar(X, PC0, Tabs0, Tabs1), 
      transfer_ref_count(X, V, Tabs1, Tabs),
      associate_vars(X, V, Aux0, Aux1) },
    gen(wait_variable(V, X), PC0, PC).	
compile_get_variable(atomic(X,T), V, PC0, PC, Tabs-Tabs, 
                                              Aux0-Aux1, 
					      Keep-Keep) --> !,
    { set_var_aux(type, V, T, Aux0, Aux1) }, 
    gen(put_constant(X, V), PC0, PC).
compile_get_variable('$SCNST'(T,Va), V, PC0, PC, Tabs-Tabs, 
                                                 Aux-Aux,
						 Keep-Keep) --> !,
    gen(put_structured_constant('$SCNST'(T,Va), V), PC0, PC).
compile_get_variable(vector(A, w), V, PC0, PC, Tabs-Tabs, 
                                               Aux0-Aux1,
					       Keep-Keep) --> !,
    { set_var_aux(type, V, vector(A), Aux0, Aux1),
      warn('Strcuture creation attempted in guard: ~w', [V=vector(A)]) },
    gen(put_vector(V, A), PC0, PC).
compile_get_variable(list(w), V, PC0, PC, Tabs-Tabs, 
                                          Aux0-Aux1,
					  Keep-Keep) --> !,
    { set_var_aux(type, V, list, Aux0, Aux1),
      warn('Strcuture creation attempted in guard: ~w', [V1=list]) },
    gen(put_list(V1), PC0, PC).
compile_get_variable(element(X,Vect,I), V, PC, PC, Tabs-Tabs, 
                                                    Aux-Aux,
					            Keep-Keep) -->
    { newvar(X, PC, Tabs, _) }, !, 
    { error('Var-var unification not implemented in guard: ~w', 
                                     [V, element(X,Vect,I)]) }.
compile_get_variable(element(X,Vect,I), V, PC0, PC, Tabs0-Tabs, 
                                                    Aux0-Aux5, 
						    Keep-Keep) --> !,
    { refvar(X, PC0, Tabs0, Tabs1), 
      transfer_ref_count(X, V, Tabs1, Tabs),
      set_var_aux(attr, X, element(Vect,I), Aux0, Aux1),
      set_var_aux(attr, V, element(Vect,I), Aux1, Aux2),
      associate_vars(X, V, Aux2, Aux3),
      set_var_aux(attr, Vect, parent(V), Aux3, Aux4),
      set_var_aux(attr, Vect, parent(X), Aux4, Aux5) },
    gen(wait_variable(V, X), PC0, PC).
compile_get_variable(V, X, PC, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) -->
    { error('Some non-implemented unification in guard: ~w', [X, V]) }.

%:- mode compile_get_value(+, +, ?, +, -, +, +, +, -, ?).
compile_get_value(var(X), V, _, PC0, PC, Tabs0-Tabs, 
                                         Aux0-Aux1,
					 Keep-Keep) -->
    { newvar(X, PC0, Tabs0, Tabs1) }, !, 
    { transfer_ref_count(V, X, Tabs1, Tabs),
      associate_vars(V, X, Aux0, Aux1) },
    gen(wait_variable(X, V), PC0, PC).
compile_get_value(var(X), V, Fail, PC0, PC, Tabs0-Tabs, 
                                            Aux0-Aux1, 
					    Keep0-PC0) --> !,
    { refvar(X, PC0, Tabs0, Tabs), 
      associate_vars(X, V, Aux0, Aux1) },
    gen(wait_value(V, X, Fail), PC0, PC).
compile_get_value(vector(A,r), V, Fail, PC0, PC, Tabs-Tabs, 
                                                 Aux0-Aux1,
						 Keep0-PC0) --> 
    { var_aux(type, V, vector, Aux0) }, !,
    { set_var_aux(type, V, vector(A), Aux0, Aux1) }, 
    gen(test_arity(A, V, Fail), PC0, PC).
compile_get_value(vector(A,r), V, Fail, PC0, PC, Tabs-Tabs, 
                                                 Aux0-Aux1,
						 Keep0-PC0) --> !,
    { set_var_aux(type, V, vector(A), Aux0, Aux1) }, 
    gen(wait_vector(V, A, Fail), PC0, PC).
compile_get_value(list(r), V, Fail, PC, PC, Tabs-Tabs, 
                                             Aux0-Aux0,
					     Keep0-Keep0) -->
    { var_aux(type, V, list, Aux0) }, !.
compile_get_value(list(r), V, Fail, PC0, PC, Tabs-Tabs, 
                                             Aux0-Aux1,
					     Keep0-PC0) --> !,
    { set_var_aux(type, V, list, Aux0, Aux1) }, 
    gen(wait_list(V, Fail), PC0, PC).
compile_get_value(atomic(X,T), V, Fail, PC0, PC, Tabs-Tabs, 
                                                 Aux0-Aux1,
						 Keep0-PC0) -->
    { var_aux(type, V, Old_Type, Aux0), 
    ( Old_Type == integer, ! ; Old_Type == float, ! ;	% 890404 Nishizaki
	Old_Type == atom ) }, !,
    { set_var_aux(type, V, T, Aux0, Aux1) }, 
    gen(wait_constant(X, V, Fail), PC0, PC).
compile_get_value(atomic(X,T), V, Fail, PC0, PC, Tabs-Tabs, 
                                                 Aux0-Aux1,
						 Keep0-PC0) --> !,
    { set_var_aux(type, V, T, Aux0, Aux1) }, 
    gen(wait_constant(X, V, Fail), PC0, PC).
compile_get_value(element(X,Vect,I), V, Fail, PC0, PC, Tabs0-Tabs, 
                                            Aux0-Aux4, 
					    Keep0-PC0) --> !,
    { refvar(X, PC0, Tabs0, Tabs), 
      set_var_aux(attr, X, element(Vect,I), Aux0, Aux1),  
      associate_vars(X, V, Aux1, Aux2),
      set_var_aux(attr, Vect, parent(X), Aux2, Aux3),
      set_var_aux(attr, Vect, parent(V), Aux3, Aux4) },
    gen(wait_value(V, X, Fail), PC0, PC).
compile_get_value(void(Data,Type), V, Fail, PC0, PC, Tabs-Tabs, 
                                                     Aux0-Aux1,
						     Keep-Keep) --> !,
    { set_var_aux(type, V, Type, Aux0, Aux1) },
    compile_indexed_argument(Type, V, Fail, PC0, PC).
compile_get_value(type(X,Type), V, _, PC0, PC, Tabs0-Tabs, 
                                               Aux0-Aux3,
				               Keep-Keep) -->
    { newvar(X, PC0, Tabs0, Tabs1) }, !, 
    { transfer_ref_count(V, X, Tabs1, Tabs),
      set_var_aux(type, V, Type, Aux0, Aux1),
      set_var_aux(type, X, Type, Aux1, Aux2),
      associate_vars(V, X, Aux2, Aux3) },
    gen(wait_variable(X, V), PC0, PC).
compile_get_value(type(X,Type), V, Fail, PC0, PC, Tabs0-Tabs, 
                                                  Aux0-Aux1, 
					          Keep0-PC0) --> 
    { refvar(X, PC0, Tabs0, Tabs), var_aux(type, V, Vtype, Aux0),
      is_var_type_same(Vtype, Type, V, X, Aux0, Aux1) }, !,
    gen(wait_value(X, V, Fail), PC0, PC).
compile_get_value(type(X,Type), V, _, PC, PC, Tabs-Tabs, 
                                              Aux-Aux, 
					      Keep-Keep) --> !,
    { var_aux(type, V, Vtype, Aux),
      error('Type mismatching occurred in ~w of ~w and ~w of ~w', 
             [Type, X, Vtype, V]) }.

%:- mode is_var_type_same(+, +, +, +, +, -).
is_var_type_same([], Type, V, X, Aux0, Aux1) :- !,
    set_var_aux(type, V, Type, Aux0, Aux1).
is_var_type_same(Vtype, [], V, X, Aux0, Aux1) :- !,
    set_var_aux(type, X, Vtype, Aux0, Aux1).
is_var_type_same(Type, Type, V, X, Aux, Aux).

%:- mode compile_indexed_argument(+, +, ?, +, -, -, ?).
compile_indexed_argument(list, V, Fail, PC0, PC) --> !,
    gen(void_list(V, Fail), PC0, PC).
compile_indexed_argument(vector(A), V, Fail, PC0, PC) --> !,
    gen(void_vector(V, A, Fail), PC0, PC).
compile_indexed_argument(Type, V, _, PC, PC) --> !.

%:- mode compile_passive_read(+, +, -, +, +, +, +, +, -, ?).
compile_passive_read(r, PC0, PC, TABS, AUX, KEEP, X, Attr) -->
    compile_read_element(X, PC0, PC, TABS, AUX, KEEP, Attr).
compile_passive_read(w, PC0, PC, TABS, AUX, Keep-Keep, X, Attr) -->
    compile_write_element(X, PC0, PC, TABS, AUX, Attr).

%:- mode compile_read_element(+, +, -, +, +, +, +, -, ?).
compile_read_element(var(X), PC0, PC, Tabs0-Tabs, 
                                      Aux0-Aux2,
                                      Keep-Keep, 
				      Attr) --> !,
    { newvar(X, PC0, Tabs0, Tabs1),
      set_attribute_and_life_time(X, Attr, PC0, Tabs1, Tabs, Aux0, Aux1),
      create_element_instruction(Attr, X, V, Inst),
      set_var_aux(attr, V, parent(X), Aux1, Aux2) },
    gen(Inst, PC0, PC).

%:- mode create_element_instruction(+, +, -, -).
create_element_instruction(car(V), X, V, read_car(V,X)) :- !.
create_element_instruction(cdr(V), X, V, read_cdr(V,X)) :- !.
create_element_instruction(vector(V,I), X, V, read_element(V,I,X)) :- !.
create_element_instruction(Attr, X, _, error_in_element(Attr,X)) :- !,
    error('Illegal element instruction: attr = ~w, var = ~w', [Attr,X]).

%:- mode compile_write_element(+, +, -, +, +, +, -, ?).
compile_write_element(var(X), PC0, PC, Tabs0-Tabs, Aux0-Aux1, Attr) -->
    { newvar(X, PC0, Tabs0, Tabs1) }, !, 
    { set_attribute_and_life_time(X, Attr, PC0, Tabs1, Tabs, Aux0, Aux1) },
    gen(write_variable(X), PC0, PC).
compile_write_element(var(X), PC0, PC, Tabs0-Tabs, Aux0-Aux1, Attr) --> !,
    { refvar(X, PC0, Tabs0, Tabs1), 
      set_attribute_and_life_time(X, Attr, PC0, Tabs1, Tabs, Aux0, Aux1) },
    gen(write_value(X), PC0, PC).
compile_write_element(atomic(X,T), PC0, PC, Tabs-Tabs, Aux-Aux, _) --> !,
    gen(write_constant(X), PC0, PC).

%:- mode compile_passive_check(+, ?, +, -, +, +, +, -, ?).
compile_passive_check(X, Fail, PC0, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) --> 
    { atom(X) }, !, { Inst =.. [X, Fail] },
    gen(Inst, PC0, PC).
compile_passive_check(X, Fail, PC, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) --> 
    { arg(1, X, Data), kl1_nonvar(Data), check_instantiated_data(X) }, !.
compile_passive_check(X, Fail, PC, PC, Tabs0-Tabs0, Aux-Aux, Keep-Keep) --> 
    { arg(1, X, Var), newvar(Var, PC, Tabs0, _) }, !,
     { error('Variable should appear in the goal argument') }.
compile_passive_check(X, Fail, PC0, PC, Tabs0-Tabs, AUX, KEEP) --> 
    { X =.. [Type,Var], refvar(Var, PC0, Tabs0, Tabs) }, 
    guard_type_code_gen(Type, Fail, PC0, PC, Var, X, AUX, KEEP).

%:- mode check_instantiated_data(+).
check_instantiated_data(integer(X)) :- integer(X), !.
check_instantiated_data(float(X))   :- float(X), !.	% 890404 Nishizaki
check_instantiated_data(atom(X))    :- atom(X), !.
check_instantiated_data(vector(X))  :- kl1_vector(X), !.
check_instantiated_data(string(X))  :- kl1_string(X), !.
check_instantiated_data(wait(X))    :- !.
check_instantiated_data(atomic(X))  :- atom(X), !.
check_instantiated_data(atomic(X))  :- integer(X), !.
check_instantiated_data(atomic(X))  :- float(X), !.	% 890404 Nishizaki
check_instantiated_data(Type) :- Type =.. [Inst, X, _],
    error('Type mismatch in guard compilation: ~w is NOT ~w', [X,Inst]).
check_instantiated_data(Type) :- Type =.. [Inst, X],    % 890911 Nishizaki
    error('Type mismatch in guard compilation: ~w is NOT ~w', [X,Inst]).

%:- mode guard_type_code_gen(+, ?, +, -, +, +, +, +, -, ?).
guard_type_code_gen((wait), _, PC, PC, Var, X, Aux-Aux, Keep0-PC) -->
    { check_var_instantiated(Var, Aux) }, !. 
guard_type_code_gen(Type, Fail, PC0, PC, Var, X, Aux0-Aux1, Keep0-PC0) -->
    { check_var_unbound(Var, Aux0) }, !, 
    { set_var_aux(type, Var, Type, Aux0, Aux1) },
    gen(check(X, Fail), PC0, PC).
guard_type_code_gen(Type, Fail, PC0, PC, Var, X, Aux0-Aux1, Keep0-PC0) -->
    { var_aux(type, Var, Old, Aux0) },
    guard_type_code_gen_1(Old, Type, PC0, PC, Var, X, Aux0-Aux1, Fail).
guard_type_code_gen(Type, _, PC, PC, V, X, Aux-Aux, Keep-Keep) -->
    { error('Type mismatch in guard compilation: ~w is NOT ~w', [V,Type]) }.

%:- mode guard_type_code_gen_1(+, +, +, -, +, +, +, ?, -, ?).
guard_type_code_gen_1((wait), Type, PC0, PC, Var, X, Aux0-Aux1, Fail) --> !,
    { set_var_aux(type, Var, Type, Aux0, Aux1) },
    gen(check(X, Fail), PC0, PC).
guard_type_code_gen_1(Old, Old, PC, PC, _, _, Aux-Aux, _) --> !.

%:- mode compile_passive_calculate(+, +, -, +, +, +, -, ?).
compile_passive_calculate(X, PC0, PC, Tabs0-Tabs, 
                                      Aux0-Aux1, 
				      Keep-Keep) -->
    { set_type_of_blt_args(X, Aux0, Aux1) }, !, 
    { functor(X, F, N), set_life_time(N, X, PC0, Tabs0, Tabs) }, 
    gen(calculate(X), PC0, PC).
compile_passive_calculate(X, PC, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) --> !,
    { error('Type mismatch in guard compilation(calculate):~n ~w', [X]) }.

%:- mode compile_passive_branch(+, +, -, +, +, +, -, ?).
compile_passive_branch(X, PC0, PC, Tabs0-Tabs,		% 890605 Nishizaki
                                      Aux0-Aux1, 
				      Keep-Keep) -->
    { set_type_of_blt_args(X, Aux0, Aux1) }, !, 
    { functor(X, F, N), set_life_time(N, X, PC0, Tabs0, Tabs) }, 
    gen(branch(X), PC0, PC).
compile_passive_branch(X, PC, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) --> !,
    { error('Type mismatch in guard compilation(branch):~n ~w', [X]) }.

%:- mode compile_passive_compare(+, ?, +, -, +, +, +, -, ?).
compile_passive_compare(true, _, PC, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) --> !.
compile_passive_compare(X, Fail, PC0, PC, Tabs0-Tabs, 
                                          Aux0-Aux1, 
					  Keep0-PC0) -->
    { set_type_of_blt_args(X, Aux0, Aux1) }, !, 
    { functor(X, F, N), set_life_time(N, X, PC0, Tabs0, Tabs) },
    gen(compare(X, Fail), PC0, PC).
compile_passive_compare(X, _, PC, PC, Tabs-Tabs, Aux-Aux, Keep-Keep) -->
    { error('Type mismatch in guard compilation(compare):~n ~w', [X]) }.
			
%:- mode set_type_of_blt_args(+, +, -).
set_type_of_blt_args(X, Type0-Attr, Type1-Attr) :- 
    builtin(X, _, _, _, TypeList, _, _), !, 
    set_type_of_one_arg(TypeList, Type0, Type1).

%:- mode set_type_of_one_arg(+, +, -).
set_type_of_one_arg([(V,T)|Cdr], Type0, Type2) :- 
    kl1_var(V), !, 
    set_var_type(Type0, V, T, Type1), 
    set_type_of_one_arg(Cdr, Type1, Type2).
set_type_of_one_arg([_|Cdr], Type0, Type1) :- !,
    set_type_of_one_arg(Cdr, Type0, Type1).
set_type_of_one_arg([], Type, Type) :- !.


%%%%% BODY COMPILATION

%:- mode compile_body(+, +, -, +, +, +, -, ?).
compile_body([], PC, PC, Tabs, Tabs, Reg-Reg) --> !.
compile_body([H|T], PC0, PC, Tabs0, Tabs, Reg0-Reg) -->
    compile_body_goal(H, PC0, PC1, Tabs0, Tabs1, Reg0-Reg1), !,
    compile_body(T, PC1, PC, Tabs1, Tabs, Reg1-Reg).

%:- mode compile_body_goal(+, +, -, +, -, +, -, ?).
compile_body_goal(V=X, PC0, PC, Tabs0, Tabs, Reg-Reg) --> !,
  ( { newvar(V, PC0, Tabs0, Tabs1) }, !,
	compile_put_variable(X, V, PC0, PC, Tabs1, Tabs);
    { refvar(V, PC0, Tabs0, Tabs1) },
	compile_general_unify(X, V, PC0, PC, Tabs1, Tabs) ).
compile_body_goal(Arg:=X, PC0, PC, Tabs0, Tabs, Reg-Reg) --> !,
    compile_set_variable(X, PC0, PC, Tabs0, Tabs, Arg).
compile_body_goal(V<=X, PC0, PC, Tabs0, Tabs, Reg-Reg) --> !,
    compile_structure_value(X, PC0, PC, Tabs0, Tabs, V).
compile_body_goal(execute_ext(X, Y), PC0, PC, Tabs0, Tabs, Reg0-Reg) --> !,
    { functor(X, F, A), 
      register_body_arguments(A, X, PC0, Tabs0-Tabs, Reg0-Reg) },
    gen(execute_ext(F/A, Y), PC0, PC).	
compile_body_goal(write(X,Attr), PC0, PC, Tabs0, Tabs, Reg-Reg) --> !,
    compile_active_write(X, PC0, PC, Tabs0, Tabs, Attr).
compile_body_goal(create_goal(X), PC0, PC, Tabs, Tabs, Reg-Reg) --> !,
    gen(create_goal(X), PC0, PC).
compile_body_goal(enqueue_goal(X), PC0, PC, Tabs, Tabs, Reg-Reg) --> !,
    gen(enqueue_goal(X), PC0, PC).
compile_body_goal(blt(X), PC0, PC, Tabs0, Tabs, Reg-Reg) --> !,
    { functor(X, F, N), set_life_time(N, X, PC0, Tabs0, Tabs) },
    gen(calculate(X), PC0, PC).
compile_body_goal(execute(X), PC0, PC, Tabs0, Tabs, Reg0-Reg) --> !,
    { functor(X, F, A),
      register_body_arguments(A, X, PC0, Tabs0-Tabs, Reg0-Reg) },
    gen(execute(F/A), PC0, PC).
compile_body_goal(proceed, PC0, PC, Tabs, Tabs, Reg-Reg) --> !,
    gen(proceed, PC0, PC).
compile_body_goal(commit, PC0, PC, Tabs, Tabs, Reg-Reg) --> !,
    gen(commit, PC0, PC).
compile_body_goal(Code, PC0, PC, Tabs0, Tabs, Reg-Reg) --> !,
  ( { arg(2, Code, Y), kl1_var(Y) }, !, 
	{ refvar(Y, PC0, Tabs0, Tabs) } ;
    { Tabs = Tabs0 } ),
    gen(Code, PC0, PC).

%:- mode register_body_arguments(+, +, +, +, +).
register_body_arguments(0, _, _, Tabs-Tabs, Reg-Reg) :- !.
register_body_arguments(K, X, PC, Tabs0-Tabs, Reg0-Reg) :-
    arg(K, X, A),
    refvar(A, PC, Tabs0, Tabs1), usereg(A, K, Reg0, Reg1),
    K1 is K-1,
    register_body_arguments(K1, X, PC, Tabs1-Tabs, Reg1-Reg).

%:- mode compile_put_variable(+, +, +, -, +, -, -, ?).
compile_put_variable(var(X), V, PC0, PC, Tabs0, Tabs) -->
    { newvar(X, PC0, Tabs0, Tabs) }, !,
    gen(put_variable(X, V), PC0, PC).
compile_put_variable(var(X), V, PC0, PC, Tabs0, Tabs) --> !,
    { refvar(X, PC0, Tabs0, Tabs) }, 
%    { associate_vars(X, V) },
    gen(put_value(X, V), PC0, PC).
compile_put_variable(vector(A), V, PC0, PC, Tabs, Tabs) --> !,
%    { set_var_type(V, vector(A)) },
    gen(put_vector(V, A), PC0, PC).
compile_put_variable(list, V, PC0, PC, Tabs, Tabs) --> !,
%    { set_var_type(V, list) },
    gen(put_list(V), PC0, PC).
compile_put_variable(atomic(X,T), V, PC0, PC, Tabs, Tabs) --> !,
%    { set_var_type(V, T) },
    gen(put_constant(X, V), PC0, PC).
compile_put_variable('$SCNST'(T,Va), V, PC0, PC, Tabs, Tabs) -->
%    { set_var_type(V, T) },
    gen(put_structured_constant('$SCNST'(T,Va),V), PC0, PC).

%:- mode compile_general_unify(+, +, +, -, +, -, -, ?).
compile_general_unify(var(X), V, PC0, PC, Tabs0, Tabs) -->
    { newvar(X, PC0, Tabs0, Tabs) }, !, 
%    { associate_vars(V, X) },
    gen(put_value(V, X), PC0, PC).
compile_general_unify(var(X), V, PC0, PC, Tabs0, Tabs) --> !,
    { refvar(X, PC0, Tabs0, Tabs) }, 
%    { associate_vars(V, X) },
    gen(get_value(X, V), PC0, PC).
compile_general_unify(vector(A), V, PC0, PC, Tabs, Tabs) --> !,
%    { set_var_type(V, vector(A)) }, 
    gen(get_vector(V, A), PC0, PC).
compile_general_unify(list, V, PC0, PC, Tabs, Tabs) --> !,
%    { set_var_type(V, list) }, 
    gen(get_list(V), PC0, PC).
compile_general_unify(atomic(X, T), V, PC0, PC, Tabs, Tabs) --> !,
%    { set_var_type(V, T) }, 
    gen(get_constant(X, V), PC0, PC).

%:- mode compile_active_write(+, +, -, +, -, +, -, ?).
compile_active_write(var(X), PC0, PC, Tabs0, Tabs, Attr) -->
    { newvar(X, PC0, Tabs0, Tabs) }, !, 
    { gen_write_variable(Attr, X, Inst) },
    gen(Inst, PC0, PC).
compile_active_write(var(X), PC0, PC, Tabs0, Tabs, Attr) --> !,
    { refvar(X, PC0, Tabs0, Tabs),
      gen_write_value(Attr, X, Inst) },
    gen(Inst, PC0, PC).
compile_active_write(atomic(X, T), PC0, PC, Tabs, Tabs, Attr) --> !,
    { gen_write_constant(Attr, X, Inst) },
    gen(Inst, PC0, PC).

%:- mode gen_write_variable(+, +, -).
gen_write_variable(car(V), X, write_car_variable(V,X)) :- !.
gen_write_variable(cdr(V), X, write_cdr_variable(V,X)) :- !.
gen_write_variable(vector(V,I), X, write_element_variable(V,I,X)) :- !.
gen_write_variable(Attr, X, error_in_write_element_variable(Attr,X)) :- !,
    error('Illegal attribute in write_variable: attr = ~w, var = ~w',
          [Attr,X]).

%:- mode gen_write_value(+, +, -).
gen_write_value(car(V), X, write_car_value(V,X)) :- !.
gen_write_value(cdr(V), X, write_cdr_value(V,X)) :- !.
gen_write_value(vector(V,I), X, write_element_value(V,I,X)) :- !.
gen_write_value(Attr, X, error_in_write_element_value(Attr,X)) :- !,
    error('Illegal attribute in write_value: attr = ~w, var = ~w',
          [Attr,X]).

%:- mode gen_write_constant(+, +, -).
gen_write_constant(car(V), X, write_car_constant(V,X)) :- !.
gen_write_constant(cdr(V), X, write_cdr_constant(V,X)) :- !.
gen_write_constant(vector(V,I), X, write_element_constant(V,I,X)) :- !.
gen_write_constant(Attr, X, error_in_write_element_constant(Attr,X)) :- !,
    error('Illegal attribute in write_constant: attr = ~w, var = ~w',
          [Attr,X]).

%:- mode compile_set_variable(+, +, -, +, -, +, -, ?).
compile_set_variable(list, PC0, PC, Tabs, Tabs, Arg) --> !,
    gen(set_list(Arg), PC0, PC).
compile_set_variable(var(V), PC0, PC, Tabs0, Tabs, Arg) -->
    { newvar(V, PC0, Tabs0, Tabs) }, !, gen(set_variable(V, Arg), PC0, PC).
compile_set_variable(var(V), PC0, PC, Tabs0, Tabs, Arg) --> !,
    { refvar(V, PC0, Tabs0, Tabs) }, gen(set_value(V, Arg), PC0, PC).
compile_set_variable(vector(N), PC0, PC, Tabs, Tabs, Arg) --> !,
    gen(set_vector(Arg, N), PC0, PC).
compile_set_variable(atomic(X,T), PC0, PC, Tabs, Tabs, Arg) --> !,
    gen(set_constant(X, Arg), PC0, PC).

%:- mode compile_structure_value(+, +, -, +, -, +, -, ?).
compile_structure_value(list(X), PC0, PC, Tabs0, Tabs, V) --> 
    { newvar(V, PC0, Tabs0, Tabs1) }, !, 
    { refvar(X, PC0, Tabs1, Tabs) }, 
%    { associate_vars(X, V) },
    gen(put_value(X, V), PC0, PC).
compile_structure_value(list(X), PC0, PC, Tabs0, Tabs, V) --> !,
    { refvar(V, PC0, Tabs0, Tabs1), refvar(X, PC0, Tabs1, Tabs) },
%     { associate_vars(X, V) },
    gen(get_list_value(X, V), PC0, PC).
compile_structure_value(vector(X), PC0, PC, Tabs0, Tabs, V) --> 
    { newvar(V, PC0, Tabs0, Tabs1) }, !, 
    { refvar(X, PC0, Tabs1, Tabs) }, 
%    { associate_vars(X, V) },
    gen(put_value(X, V), PC0, PC).
compile_structure_value(vector(X), PC0, PC, Tabs0, Tabs, V) --> !,
    { refvar(V, PC0, Tabs0, Tabs1), refvar(X, PC0, Tabs1, Tabs) },
%    { associate_vars(X, V) },
    gen(get_vector_value(X, V), PC0, PC).


