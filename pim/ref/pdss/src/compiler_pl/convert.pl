%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%:- mode convert_one_clause(+, -, +, -).
convert_one_clause((H0:-G0|B0), (H:-G|B), Nv0, Nv1) :- !,
    convert_one_goal(head, H0, H, Vl0, Vl1),
    convert_goals(G0, G, Vl1, Vl2, guard),
    convert_goals(B0, B, Vl2, [], body),
    create_kl1_var_loop(Vl0, Nv0, Nv1).
convert_one_clause((H0:-B0), (H:-true|B), Nv0, Nv1) :- !,
    convert_one_goal(head, H0, H, Vl0, Vl1),
    convert_goals(B0, B, Vl1, [], body),
    create_kl1_var_loop(Vl0, Nv0, Nv1).
convert_one_clause(H0, (H:-true|true), Nv0, Nv1) :- 
    convert_one_goal(head, H0, H, Vl0, []),
    create_kl1_var_loop(Vl0, Nv0, Nv1).

%:- mode convert_goals(+, -, -, ?, +).
convert_goals((A0,B0), (A,B), Vl0, Vl2, Part) :- !,
    convert_goals(A0, A, Vl0, Vl1, Part),
    convert_goals(B0, B, Vl1, Vl2, Part).
convert_goals(A0, A, Vl0, Vl1, Part) :- !,
    convert_one_goal(Part, A0, A, Vl0, Vl1).

%:- mode convert_one_goal(+, +, -, -, ?).
convert_one_goal(body, P0, P, Vl0, Vl1) :- !,
    convert_one_body_goal(P0, P, Vl0, Vl1).
convert_one_goal(guard, X=Y, true, Vl, Vl) :-              % 88.09.09 Y.K.
    check_if_arg_var_and_atomic(X, Y), !,
    X = Y.
convert_one_goal(Part, P0, P, Vl0, Vl1) :- functor(P0, F, A), !,
    functor(P, F, A),
    convert_goal_args(A, P0, P, Vl0, Vl1, Part).

%:- mode check_if_arg_var_and_atomic(?, ?).
check_if_arg_var_and_atomic(X, Y) :- var(X), atomic(Y), !.
check_if_arg_var_and_atomic(X, Y) :- atomic(X), var(X), !.

%:- mode convert_one_body_goal(+, -, -, ?).
convert_one_body_goal(M:P0, M:P, Vl0, Vl) :- !,
    convert_one_body_goal(P0, P, Vl0, Vl).
convert_one_body_goal(P0@Pri, P@Pri, Vl0, Vl) :- !,
    convert_one_body_goal(P0, P, Vl0, Vl).
convert_one_body_goal('#atom_talbe#'(T0),                   % 88.09.21. Y.K.
			(T = '$SCNST'(atom_table,[])),Vl0,Vl) :-
    check_if_this_is_legal_builtin(pimos), !,
    convert_one_goal_arg(T0, T, Vl0, Vl, body, _).
convert_one_body_goal('#module_talbe#'(T0),                 % 88.09.21. Y.K.
			(T = '$SCNST'(module_table,[])),Vl0,Vl) :-
    check_if_this_is_legal_builtin(pimos), !,
    convert_one_goal_arg(T0, T, Vl0, Vl, body, _).
convert_one_body_goal(P0, P, Vl0, Vl) :- !,
    functor(P0, F, A), functor(P, F, A),
    convert_goal_args(A, P0, P, Vl0, Vl, body).

%:- mode convert_goal_args(+, +, +, -, ?, +).
convert_goal_args(0, P0, P, Vl, Vl, _) :- !.
convert_goal_args(A, P0, P, Vl0, Vl2, Part) :- !,
    arg(A, P0, E0),
    convert_one_goal_arg(E0, E, Vl0, Vl1, Part, _),
    arg(A, P, E),
    A1 is A-1,
    convert_goal_args(A1, P0, P, Vl1, Vl2, Part).

%:- mode convert_one_goal_arg(?, -, -, ?, +, -).
convert_one_goal_arg(E0, E0, [E0|Vl], Vl, _, 0) :- var(E0), !.
convert_one_goal_arg([], [], Vl, Vl, _, 1) :- !.
convert_one_goal_arg({}, {}, Vl, Vl, _, 1) :- !.           % 88.09.19 Y.K.
convert_one_goal_arg(E0, E0, Vl, Vl, _, 1) :- atomic(E0), !.
convert_one_goal_arg(E0, E, Vl0, Vl1, Part, Flag) :- functor(E0, F, A), !,
    convert_one_structure_arg(F, A, Vl0, Vl1, E0, E, Part, Flag).

%:- mode convert_one_structure_arg(+, +, -, ?, +, -, +, -).
convert_one_structure_arg('.', 2, Vl0, Vl1, E0, E, Part, Flag) :- !,
    functor(E1, '$LIST', 2),
    convert_to_normal_structure(2, E0, E1, Vl0, Vl1, Part, 1-Flag),
    check_if_constant(Part, Flag, E1, E).
convert_one_structure_arg('{}', 1, Vl0, Vl1, E0, E, Part, Flag) :- !,
    arg(1, E0, E1),
    flatten_vector_structure(E1, E2, []),
    E3 =.. ['$VECT'|E2], functor(E3, _, A),
    functor(E4, '$VECT', A),
    convert_to_normal_structure(A, E3, E4, Vl0, Vl1, Part, 1-Flag),
    check_if_constant(Part, Flag, E4, E).
% 890511 Nishizaki
convert_one_structure_arg('#', 2, Vl, Vl, E0, '$SCNST'(Type,Data), _, 1) :-
    arg(1, E0, Type), Type==ascii, arg(2, E0, Data), ascii_string(Data), !.
convert_one_structure_arg('#', 2, Vl, Vl, E0, '$SCNST'(Type,Data), _, 1) :-
    arg(1, E0, Type), Type==string, arg(2, E0, Data), ascii_string(Data), !.
convert_one_structure_arg('#', 2, Vl, Vl, E0, '$SCNST'(Type,Data), _, 1) :-
    arg(1, E0, Type), Type==(module), arg(2, E0, Data), atomic(Data), !.
convert_one_structure_arg(F, A, Vl0, Vl1, E0, E, Part, Flag) :- 
    A1 is A+1,
    E0 =.. E0_List, E1 =.. ['$VECT'|E0_List],
    functor(E2, '$VECT', A1),
    convert_to_normal_structure(A1, E1, E2, Vl0, Vl1, Part, 1-Flag),
    check_if_constant(Part, Flag, E2, E).

%:- mode flatten_vector_structure(?, -, ?).
flatten_vector_structure(A, [A|Cdr], Cdr) :- var(A), !.
flatten_vector_structure((A,B), E0, E2) :- !,
    flatten_vector_structure(A, E0, E1),
    flatten_vector_structure(B, E1, E2).
flatten_vector_structure(E, [E|Cdr], Cdr) :- !.

%:- mode convert_to_normal_structure(+, +, +, -, ?, +, +).
convert_to_normal_structure(0, _, _, Vl, Vl, _, Flag-Flag) :- !.
convert_to_normal_structure(A, V0, V1, Vl0, Vl2, Part, Flag0-Flag3) :-
    arg(A, V0, E0),
    convert_one_goal_arg(E0, E1, Vl0, Vl1, Part, Flag1),
  ( E1 == {}, Part == body, !,			% 890810 Nishizaki
	check_if_constant(Part, 1, '$VECT', E2); % 890608 Nishizaki
    E2 = E1),
    Flag2 is Flag0 /\ Flag1,
    arg(A, V1, E2),
    A1 is A-1,
    convert_to_normal_structure(A1, V0, V1, Vl1, Vl2, Part, Flag2-Flag3).

%:- mode check_if_constant(+, +, +, -).
%check_if_constant(_, _, V, V) :- !.       % suppress SCNST 88.08.03 Y.K
check_if_constant(head,  _, V, V) :- !.
check_if_constant(guard, _, V, V) :- !.
check_if_constant(body,  1, V, '$SCNST'(Type,V)) :- !, 
    functor(V, F, A), Type =.. [F,A].
check_if_constant(_,    0, V, V) :- !.

%:- mode create_kl1_var_loop(+, +, -).
create_kl1_var_loop([], Nv, Nv) :- !.
create_kl1_var_loop([One|Cdr], Nv0, Nv2) :- var(One), !,
    create_kl1_var(One, Nv0, Nv1),
    create_kl1_var_loop(Cdr, Nv1, Nv2).
create_kl1_var_loop([One|Cdr], Nv0, Nv1) :- kl1_var(One), !,
    create_kl1_var_loop(Cdr, Nv0, Nv1).
create_kl1_var_loop([One|Cdr], Nv0, Nv1) :- atomic(One), !,
    create_kl1_var_loop(Cdr, Nv0, Nv1).

