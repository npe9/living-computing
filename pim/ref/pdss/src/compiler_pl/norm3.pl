%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% NORMALIZATION

:- mode normalize(+, -, ?, -, +).
normalize((H0:-G0|B0), H, G, B, N0-Nv) :- !,
    functor(H0, F, A), functor(H, F, A),
    normalize_head_args(0, A, H0, H, G-G1, []-Vt, N0-N1),
    normalize_guard(G0, G1, [], N1-N2), 
    classify_body(B0, BU-BB, BB-[], BG-[], Vt, N2-N3),
    normalize_body_builtin(BU, B, B1, N3-N4),
    normalize_body(BG, B1, [], N4-Nv).
normalize((H0:-B0), H, G, B, Nv) :- !,
    normalize((H0:-true|B0), H, G, B, Nv).
normalize(H0, H, G, B, Nv) :-
    normalize((H0:-true|true), H, G, B, Nv).

:- mode normalize_head_args(+, +, +, +, +, +, +).
normalize_head_args(A, A, _, _, Gh-Gh, Vt-Vt, N-N) :- !.
normalize_head_args(K, A, H0, H, Gh0-Gh2, Vt0-Vt2, N0-N3) :- 
    K1 is K+1, 
    arg(K1, H0, E0), 
    create_kl1_var(E, N0, N1), arg(K1, H, E), 
    normalize_guard_unify(E0, E, Gh0, Gh1, N1-N2),
    intern_new_variable_table(E0, Vt0, Vt1),
    normalize_head_args(K1, A, H0, H, Gh1-Gh2, Vt1-Vt2, N2-N3).

:- mode intern_new_variable_table(+, +, -).
intern_new_variable_table(E0, Vt, Vt) :- 
    kl1_var(E0), is_head_var_interned(Vt, E0), !.
intern_new_variable_table(E0, Vt, [(E0,_)|Vt]) :- 
    kl1_var(E0), !.
intern_new_variable_table(E0, Vt, Vt) :- !.

:- mode is_head_var_interned(+, +).
is_head_var_interned([], _) :- !, fail.
is_head_var_interned([(E,_)|Cdr], E) :- !.
is_head_var_interned([_|Cdr], E) :- !, is_head_var_interned(Cdr, E).

:- mode normalize_guard(+, ?, ?, +).
normalize_guard(true, G, G, N-N) :- !.
normalize_guard(X=Y, G0, G, N0N1) :- !, 
    normalize_guard_unify(X, Y, G0, G, N0N1).
normalize_guard((X,Y), G0, G2, N0-N2) :- !,
    normalize_guard(X, G0, G1, N0-N1), 
    normalize_guard(Y, G1, G2, N1-N2).
normalize_guard(X0, G0, G, N0N1) :- 
    builtin(X0, In, Out, Pres, Dtype, Btype, Comp_mode),
    check_if_this_is_legal_builtin(Comp_mode), !,
    normalize_builtin(Btype, X0, In, Out, Pres, G0, G, N0N1).
normalize_guard(X, G, G, N-N) :- 
    error('Guard goal not implemented: ~w', [X]).

:- mode normalize_builtin(+, +, +, +, +, -, ?, +).
normalize_builtin(check, X, In, _, Pres, G0, G1, N0N1) :- !,
    set_preceding_builtin(Pres, G0, [check(X)|G1], N0N1).
normalize_builtin(compare, X0, In, _, Pres, G0, G2, N0-N2) :- !,
    functor(X0, F, A), functor(X, F, A),
    set_preceding_builtin(Pres, G0, G1, N0-N1),
    normalize_builtin_input_args(In, X0, X, G1, [compare(X)|G2], N1-N2).
normalize_builtin(calculate, X0, In, Out, Pres, G0, G3, N0-N3) :-
    functor(X0, F, N), functor(X, F, N),    
    set_preceding_builtin(Pres, G0, G1, N0-N1),
    normalize_builtin_input_args(In, X0, X, G1, [calculate(X)|G2], N1-N2),    
    normalize_builtin_output_args(Out, X0, X, G2, G3, N2-N3).
normalize_builtin(branch, X0, In, Out, Pres, G0, G3, N0-N3) :-%890605 Nishizaki
    functor(X0, F, N), functor(X, F, N),    
    set_preceding_builtin(Pres, G0, G1, N0-N1),
    normalize_builtin_input_args(In, X0, X, G1, [branch(X)|G2], N1-N2),    
    normalize_builtin_output_args(Out, X0, X, G2, G3, N2-N3).

:- mode set_preceding_builtin(+, -, ?, +).
set_preceding_builtin([One|Next], G0, G2, N0-N2) :-
    builtin(One, In, Out, Pres, Dtype, Btype, _), !, 
    normalize_builtin(Btype, One, In, Out, Pres, G0, G1, N0-N1),
    set_preceding_builtin(Next, G1, G2, N1-N2).
set_preceding_builtin([], G, G, N-N) :- !.

:- mode normalize_builtin_input_args(+, +, +, ?, ?, +).
normalize_builtin_input_args([], _, _, G, G, N-N) :- !.
normalize_builtin_input_args([In|Y], H0, H, G0, G, N0-N2) :-
    arg(In, H0, X0), arg(In, H, X),
    normalize_builtin_input_one_arg(X0, X, G0, G1, N0-N1),
    normalize_builtin_input_args(Y, H0, H, G1, G, N1-N2).

:- mode normalize_builtin_input_one_arg(+, ?, -, ?, +).
normalize_builtin_input_one_arg(X0, X0, G, G, N-N) :- kl1_var(X0), !. 
normalize_builtin_input_one_arg(X0, X, G0, G, N0-N2) :- atomic(X0), !,
    create_kl1_var(X, N0, N1),
    normalize_guard_unify(X, X0, G0, G, N1-N2).
normalize_builtin_input_one_arg(X0, X, G0, G, N0-N2) :- 
    functor(X0, #, 2), !,
    create_kl1_var(X, N0, N1),
    normalize_guard_unify(X, X0, G0, G, N1-N2).
normalize_builtin_input_one_arg(X0, X, G0, G, N0-N2) :-     % 88.08.29 Y.K.
    functor(X0, '$SCNST', 2), !, create_kl1_var(X, N0, N1),
    normalize_guard_unify(X, X0, G0, G, N1-N2).
normalize_builtin_input_one_arg(X0, X, G0, G, N0-N3) :- 
    functor(X0, _, _), !, create_kl1_var(X, N0, N1),
    expand_guard_macro(X0, Res, G0, G1, N1-N2),
    normalize_guard_unify(X, Res, G1, G, N2-N3).

:- mode normalize_builtin_output_args(+, +, +, ?, ?, +).
normalize_builtin_output_args([], _, _, G, G, N-N) :- !.
normalize_builtin_output_args([Out|Y], H0, H, G0, G, N0-N3) :- 
    arg(Out, H0, X0), 
    arg(Out, H, X), create_kl1_var(X, N0, N1),
    check_if_vector_element(H, X, X1),
    normalize_guard_unify(X1, X0, G0, G1, N1-N2), !,
    normalize_builtin_output_args(Y, H0, H, G1, G, N2-N3).

:- mode check_if_vector_element(+, +, -).
check_if_vector_element(vector_element(V,I,E), _, '$ELEMENT'(E,V,I)) :- !.
check_if_vector_element(_, E, E) :- !.

:- mode expand_guard_macro(+, -, -, ?, +).
expand_guard_macro(X0, Res, G0, G, N0N1) :- 
    builtin(X0, In, [Out], Pres, Dtype, Btype, _), !, 
    arg(Out, X, Res),
    normalize_builtin(Btype, X0, In, [Out], Pres, G0, G, N0N1).
expand_guard_macro(X0, Res, G, G, N-N) :- 
% error('Macro expansion failed in guard: ~w', [X0]).
    error('Explicit structure is not implemented in gurad builtin input argument: ~w', [X0]).	% 900710 Nishizaki

:- mode normalize_guard_unify(+, ?, -, ?, +).
normalize_guard_unify(X0, Y0, G0, G, N0N1) :-		% vector_element/3
    functor(X0, '$ELEMENT', 3), !,
    normalize_guard_element_unify(Y0, X0, G0, G, N0N1).
normalize_guard_unify(X, Y, G0, G, N0N1) :- kl1_var(X), !,
    normalize_variable_unify(Y, X, G0, G, N0N1).
normalize_guard_unify(Y, X, G0, G, N0N1) :- kl1_var(X), !,
    normalize_variable_unify(Y, X, G0, G, N0N1).
normalize_guard_unify(X0, Y0, G0, G, N0N1) :-		% struct vs. struct
    functor(X0, F, A), functor(Y0, F, A), !,		% unification
    normalize_struct_unify(0, A, X0, Y0, G0, G, N0N1).
normalize_guard_unify(X, Y, G, G, N-N) :-
    error('Guard goal always fails: ~w', [X=Y]).

:- mode normalize_variable_unify(+, +, -, ?, +).
normalize_variable_unify(X, V, [V=var(X)|G], G, N-N) :- kl1_var(X), !.
normalize_variable_unify(X, V, [V=atomic(X,T)|G], G, N-N) :- 
    atomic(X), X \== {}, !, kl1_type_of(X, T).
normalize_variable_unify(X, V, G0, G, N0N1) :- functor(X, F, A), !,
    normalize_guard_structure(F, V, G0, G, N0N1, X).
normalize_variable_unify(X, V, G, G, N-N) :-
    error('Guard goal always fails: ~w', [V=X]).

:- mode normalize_guard_element_unify(+, +, -, ?, +).       % 88.08.25 Y.K.
normalize_guard_element_unify(Y0, X0, [Y0=X|G], G, N-N) :-
    kl1_var(Y0), !,
    X0 =.. [_|Operand], X =.. [element|Operand].
normalize_guard_element_unify(Y0, X0, [Y=X|G0], G, N0-N2) :- !,
    create_kl1_var(Y, N0, N1),
    X0 =.. [_|Operand], X =.. [element|Operand],
    normalize_variable_unify(Y0, Y, G0, G, N1-N2).

:- mode normalize_variable_unify_list(+, -, ?, +).
normalize_variable_unify_list([], G, G, N-N) :- !.
normalize_variable_unify_list([V=X|Cdr], G0, G, N0-N2) :-
    normalize_variable_unify(X, V, G0, G1, N0-N1),
    normalize_variable_unify_list(Cdr, G1, G, N1-N2).

:- mode normalize_guard_structure(+, +, -, ?, +, +).
normalize_guard_structure('$LIST', V, [V=list(M)|G0], G, N0N1, X) :- !,
    normalize_list_args(X, V, G0, G, N0N1, M).
normalize_guard_structure('$VECT', V, [V=vector(A,M)|G0], G, N0N1, X) :- !,
    functor(X, _, A),
    normalize_structure_args(0, A, X, V, G0, G, [], N0N1, M).	
normalize_guard_structure('@', V, G0, G, N0N1, X) :-
    arg(1, X, Flag), is_indexing_flag(Flag), !, 
    arg(2, X, IndexedArg),
    normalize_indexed_arg(Flag, V, G0, G, N0N1, IndexedArg).
normalize_guard_structure('$SCNST', V, [V0=X,check(wait(V0)),V=var(V0)|G], 
                                       G, N0-N1, X) :- !,
    create_kl1_var(V0, N0, N1).
normalize_guard_structure(F, V, [V=vector(A,M)|G0], G, N0N1, X) :- !,
    functor(X, _, A),
    normalize_structure_args(0, A, X, V, G0, G, [], N0N1, M).	

:- mode normalize_indexed_arg(+, +, -, ?, +, +).
normalize_indexed_arg('$VOID', V, [V=void(X,T)|G], G, N-N, X) :- !,
    kl1_type_of(X, T).    
normalize_indexed_arg('$LIST', V, [V=void(X,list)|G0], G, N0N1, X) :-
    normalize_list_args(X, V, G0, G, N0N1, M).    
normalize_indexed_arg('$VECT', V, [V=void(X,vector(A))|G0], G, N0N1, X) :-
    functor(X, _, A),
    normalize_structure_args(0, A, X, V, G0, G, [], N0N1, M).	
normalize_indexed_arg('$WAIT', V, [V=type(X,(wait))|G], G, N-N, X) :- !.
normalize_indexed_arg('$TYPE'(Type), V, [V=type(X,Type)|G], G, N-N, X) :- !.

:- mode normalize_list_args(+, +, -, ?, +, -).
normalize_list_args(X, V, G0, G, N0-N3, M) :-
    arg(1, X, Car),
    normalize_one_arg(Car, car(V), G0, G1, [], D0, N0-N1, M),
    arg(2, X, Cdr),
    normalize_one_arg(Cdr, cdr(V), G1, G2, D0, D, N1-N2, M),
    normalize_variable_unify_list(D, G2, G, N2-N3).

:- mode normalize_structure_args(+, +, +, +, ?, ?, ?, +, -).
normalize_structure_args(A, A, _, _, G0, G, D, N0N1, M) :- !,
    normalize_variable_unify_list(D, G0, G, N0N1).
normalize_structure_args(I, A, X, V, G0, G, D0, N0-N2, M) :-
    I1 is I+1, arg(I1, X, E), 
    normalize_one_arg(E, vector(V,I), G0, G1, D0, D, N0-N1, M),
    normalize_structure_args(I1, A, X, V, G1, G, D, N1-N2, M).

:- mode normalize_one_arg(+, +, -, ?, +, ?, +, -).
normalize_one_arg('$VOID'@X, Attr, G, G, D, D, N-N, M) :- !.
normalize_one_arg(X, Attr, [read(var(New),Attr,M),New=var(X)|G], G, 
                                                        D, D, N0-N1, M) :- 
    kl1_var(X), !, create_kl1_var(New, N0, N1).
normalize_one_arg(X, Attr, [read(var(New),Attr,M),New=atomic(X,T)|G], G, 
                                                        D, D, N0-N1, M) :- 
    atomic(X), X \== {}, !, 
    kl1_type_of(X, T), create_kl1_var(New, N0, N1).
normalize_one_arg(X, Attr, [read(var(V),Attr,M)|G], G, D, [V=X|D], N0-N1, M) :-
    create_kl1_var(V, N0, N1).

:- mode normalize_struct_unify(+, +, +, +, -, ?, +).
normalize_struct_unify(A, A, _, _, G, G, N-N) :- !.
normalize_struct_unify(I, A, X, Y, G0, G, N0-N2) :- 
    I1 is I+1, arg(I1, X, Xe), arg(I1, Y, Ye), 
    normalize_guard_unify(Xe, Ye, G0, G1, N0-N1),
    normalize_struct_unify(I1, A, X, Y, G1, G, N1-N2).


%%%%% BODY NORMALIZATION

:- mode classify_body(+, +, +, +, +, +).
classify_body(true, U-U, B-B, G-G, _, N-N) :- !.
classify_body((X,Y), U0-U, B0-B, G0-G, Vt, N0-N2) :- !,
    classify_body(X, U0-U1, B0-B1, G1-G, Vt, N0-N1),
    classify_body(Y, U1-U,  B1-B, G0-G1, Vt, N1-N2).
classify_body(X=Y, U0-U1, [New|B]-B, G-G, Vt, N0N1) :- !,
    convert_body_goal_variables(X=Y, U0-U1, New, Vt, N0N1).
classify_body(X,   U0-U1, [New|B]-B, G-G, Vt, N0N1) :- 
    functor(X, F, A), body_blt(F, A, _, _, _, Comp_mode), 
    check_if_this_is_legal_builtin(Comp_mode), !,
    convert_body_goal_variables(X, U0-U1, New, Vt, N0N1).
classify_body(X, U0-U1, B-B, [New|G]-G, Vt, N0N1) :- !,
    convert_body_goal_variables(X, U0-U1, New, Vt, N0N1).

:- mode convert_body_goal_variables(+, +, -, +, +).
convert_body_goal_variables(X, U-U, X, Vt, N-N) :- atomic(X), !.
convert_body_goal_variables(X, UU, New, Vt, N0N1) :- kl1_var(X), !,
    convert_one_variable(Vt, X, UU, New, N0N1).
convert_body_goal_variables(X, U-U, X, Vt, N-N) :- 
    functor(X, '$SCNST', A), !.
convert_body_goal_variables(X, UU, New, Vt, N0N1) :- 
    functor(X, F, A), !,
    functor(New, F, A),
    convert_body_goal_variables_1(0, A, X, New, UU, Vt, N0N1).

:- mode convert_body_goal_variables_1(+, +, +, +, +, +, +).
convert_body_goal_variables_1(A, A, X, New, U-U, Vt, N-N) :- !.
convert_body_goal_variables_1(K, A, X, New, U0-U2, Vt, N0-N2) :- 
    K1 is K+1, arg(K1, X, E0), 
    convert_body_goal_variables(E0, U0-U1, E, Vt, N0-N1),
    arg(K1, New, E),
    convert_body_goal_variables_1(K1, A, X, New, U1-U2, Vt, N1-N2).

:- mode convert_one_variable(+, +, +, -, +).
convert_one_variable([], X, U-U, X, N-N) :- !.
convert_one_variable([(X,New)|Vt], X, [X=New|U]-U, New, N0-N1) :- 
    var(New), !,
    create_kl1_var(New, N0, N1).
convert_one_variable([(X,New)|Vt], X, U-U, New, N-N) :- !.
convert_one_variable([_|Vt], X, UU, New, N0N1) :- !,
    convert_one_variable(Vt, X, UU, New, N0N1).


%%%%% NORMALIZATION OF BODY BUILTIN PREDICATES

:- mode normalize_body_builtin(+, -, ?, +).
normalize_body_builtin([], B, B, N-N) :- !.
normalize_body_builtin([X=Y|Cdr], B0, B2, N0-N2) :- !,
    normalize_active_unification(X, Y, B0, B1, N0-N1),    
    normalize_body_builtin(Cdr, B1, B2, N1-N2).
normalize_body_builtin([Blt0|Cdr], B0, B3, N0-N3) :- 
    functor(Blt0, BltName0, A), 
    body_blt(BltName0, A, BltName, In, Unify, _), !,
    functor(Blt, BltName, A),
    normalize_blt_input_args(In, Blt0, Blt, B0, [blt(Blt)|B1], N0-N1),
    normalize_blt_output_args(Unify, Blt0, Blt, B1, B2, N1-N2),
    normalize_body_builtin(Cdr, B2, B3, N2-N3).
normalize_body_builtin([Blt|Cdr], B, B, N-N) :- 
    error('Body builtin not implemented: ~w', [Blt]).

:- mode normalize_body_blt(+, +, +, -, ?, +).
normalize_body_blt(Blt0, In, Unify, B0, B2, N0-N2) :- 
    functor(Blt0, F0, A),
    body_blt(F0, A, F, In, Unify, _), !,
    functor(Blt, F, A),
    normalize_blt_input_args(In, Blt0, Blt, B0, [blt(Blt)|B1], N0-N1),
    normalize_blt_output_args(Unify, Blt0, Blt, B1, B2, N1-N2).

:- mode normalize_blt_input_args(+, +, +, ?, ?, +).
normalize_blt_input_args([], _, _, G, G, N-N) :- !.
normalize_blt_input_args([I0|Y], H0, H, G0, G, N0-N2) :-
    arg(I0, H0, X0), arg(I0, H, X),
    normalize_blt_input_one_arg(X0, X, G0, G1, N0-N1),
    normalize_blt_input_args(Y, H0, H, G1, G, N1-N2).

:- mode normalize_blt_input_one_arg(+, -, -, ?, +).
normalize_blt_input_one_arg(X0, X, [X0=var(X)|G], G, N0-N1) :- 
    kl1_var(X0), !,                                         % 880609
    create_kl1_var(X, N0, N1).
normalize_blt_input_one_arg(X0, X, G0, G, N0-N2) :- 
    atomic(X0), X0 \== {}, !, 
    create_kl1_var(X, N0, N1),
    normalize_argument_put(X0, X, G0, G, N1-N2).
normalize_blt_input_one_arg(X0, X, G0, G, N0-N2) :- 
    functor(X0, _, _), !,
    create_kl1_var(X, N0, N1),
    normalize_argument_put(X0, X, G0, G, N1-N2).

:- mode normalize_blt_output_args(+, +, +, ?, ?, +).
normalize_blt_output_args([], _, _, G, G, N-N) :- !.
normalize_blt_output_args([I0|Y], H0, H, G0, G, N0-N3) :- 
    arg(I0, H0, X0), create_kl1_var(X, N0, N1),
    arg(I0, H, X), 
    normalize_active_unify(X0, X, G0, G1, N1-N2), !,
    normalize_blt_output_args(Y, H0, H, G1, G, N2-N3).

:- mode expand_body_macro(+, -, -, ?, +).
expand_body_macro(X0, Res, G0, G, N0-N1) :- 
    functor(X0, F0, A),
    body_blt(X0, A, F, In, [Unify], _), !,
    functor(X, F, A),
    arg(Unify, X, Res),
    normalize_body_blt(X, In, [Unify], G0, G, N0N1).
expand_body_macro(X0, Res, G, G, N-N) :- 
    error('Macro expansion failed in body: ~w', [X0]).


%%%%% NORMALIZATION OF BODY USER GOALS

:- mode normalize_body(+, -, ?, +).
normalize_body([], [proceed|B], B, N-N) :- !.
normalize_body([X], B0, B, N0N1) :- !,
    normalize_body_last_goal(X, B0, B, N0N1).
normalize_body([X|T], B0, B, N0-N2) :-
    normalize_body_goal(X, B0, B1, N0-N1), !,
    normalize_body(T, B1, B, N1-N2).

:- mode normalize_body_last_goal(+, -, ?, +).
normalize_body_last_goal((M:G0), B0, B1, N0N1) :- !, 
    calculate_module(M, M1), 
    normalize_execute_goal_args(G0, G1, B0, [execute_ext(G1,M1)|B1], N0N1).
normalize_body_last_goal((G@P), B0, B1, N0N1) :- !, 
    normalize_by_pragma(P, G, B0, [proceed|B1], N0N1).
normalize_body_last_goal(G0, B0, B1, N0N1) :- !, 
    normalize_execute_goal_args(G0, G1, B0, [execute(G1)|B1], N0N1).

:- mode normalize_body_goal(+, -, ?, +).
normalize_body_goal((M:G0), [create_ext(F/A,M1)|B0], B1, N0N1) :- !, 
    functor(G0, F, A),
    calculate_module(M, M1), 
    normalize_body_set_args(0, A, G0, B0, [enqueue_ext(F/A,M1)|B1], N0N1).
normalize_body_goal((G@P), B0, B1, N0N1) :- !, 
    normalize_by_pragma(P, G, B0, B1, N0N1).
normalize_body_goal(G0, [create_goal(F/A)|B0], B, N0N1) :- !, 
    functor(G0, F, A), 
    normalize_body_set_args(0, A, G0, B0, [enqueue_goal(F/A)|B], N0N1).

:- mode normalize_by_pragma(+, +, -, ?, +).
normalize_by_pragma(priority(Op, Val), G, B0, B2, N0-N2) :- !,
    functor(G, F, A),
    calculate_priority(Op, Val, Pri, B0, 
				[create_with_priority(F/A,Pri)|B1], N0-N1),
    normalize_body_set_args(0, A, G, B1, 
				[enqueue_with_priority(F/A,Pri)|B2], N1-N2).
normalize_by_pragma(processor(R), G, B0, B2, N0-N2) :- !,
    functor(G, F, A),
    calculate_processor(R, Reg, B0, [create_to_processor(F/A,Reg)|B1], N0-N1),
    normalize_body_set_args(0, A, G, B1, 
				[enqueue_to_processor(F/A,Reg)|B2], N1-N2).
normalize_by_pragma(node(R), G, B0, B2, N0-N2) :- !,
    functor(G, F, A),
    calculate_node(R, Reg, B0, [create_to_node(F/A,Reg)|B1], N0-N1),
    normalize_body_set_args(0, A, G, B1, 
				[enqueue_to_node(F/A,Reg)|B2], N1-N2).
normalize_by_pragma(X, G, B, B, N-N) :- !,
    error('Invalid pragma specification: ~w', [X]).

:- mode calculate_module(+, -).
calculate_module(M, M) :- atom(M), !.
calculate_module(M, []) :- 
    error('Invalid module specification:~w', [M]).

:- mode calculate_priority(+, ?, -, -, ?, +).
calculate_priority('*', In, Res, B0, B, N0-N2) :- 
    var(In), !, create_kl1_var(In, N0, N1), create_kl1_var(Res, N1, N2),
    normalize_body_builtin(['RATE'(In,Res)], B0, B, N2-N3). % 90.2.6 Nishizaki
calculate_priority('*', In, Res, B0, B, N0-N2) :- 
    kl1_var(In), !, create_kl1_var(Res, N0, N1),
    normalize_body_builtin(['RATE'(In,Res)], B0, B, N1-N2). % 90.2.6 Nishizaki
calculate_priority('*', In, Res, B0, B, N0-N2) :- 
    atomic(In), !, create_kl1_var(Res, N0, N1),
    normalize_body_builtin(['RATE'(In,Res)], B0, B, N1-N2). % 90.2.6 Nishizaki
calculate_priority('$', In, Res, B0, B, N0-N3) :-
    var(In), !, create_kl1_var(In, N0, N1), create_kl1_var(Res, N1, N2),
    normalize_body_builtin(['RLTV'(In,Res)], B0, B, N2-N3). % 90.2.6 Nishizaki
calculate_priority('$', In, Res, B0, B, N0-N2) :-
    kl1_var(In), !, create_kl1_var(Res, N0, N1),
    normalize_body_builtin(['RLTV'(In,Res)], B0, B, N1-N2). % 90.2.6 Nishizaki
calculate_priority('$', In, Res, B0, B, N0-N2) :-
    atomic(In), !, create_kl1_var(Res, N0, N1),
    normalize_body_builtin(['RLTV'(In,Res)], B0, B, N1-N2). % 90.2.6 Nishizaki
calculate_priority(X, Y, Res, B, B, N-N) :- 
    error('Invalid priority specification: ~w', [priority(X,Y)]).

:- mode calculate_processor(?, -, -, ?, +).
calculate_processor(R, Reg, [Reg=var(R)|B], B, N0-N2) :- var(R), !,
    create_kl1_var(Reg, N0, N1), create_kl1_var(R, N1, N2).
calculate_processor(R, Reg, [Reg=var(R)|B], B, N0-N1) :- kl1_var(R), !,
    create_kl1_var(Reg, N0, N1).
calculate_processor(R, Reg, [Reg=atomic(R,T)|B], B, N0-N1) :- atomic(R), !,
    kl1_type_of(R, T), create_kl1_var(Reg, N0, N1).
calculate_processor(X, Res, B, B, N-N) :- 
    error('Invalid processor specification:~w', [processor(X)]).

:- mode calculate_node(?, -, -, ?, +).
calculate_node(R, Reg, [Reg=var(R)|B], B, N0-N2) :- var(R), !,
    create_kl1_var(Reg, N0, N1), create_kl1_var(R, N1, N2).
calculate_node(R, Reg, [Reg=var(R)|B], B, N0-N1) :- kl1_var(R), !,
    create_kl1_var(Reg, N0, N1).
calculate_node(R, Reg, [Reg=atomic(R,T)|B], B, N0-N1) :- atomic(R), !,
    kl1_type_of(R, T), create_kl1_var(Reg, N0, N1).
calculate_node(X, Res, B, B, N-N) :- 
    error('Invalid node specification:~w', [node(X)]).


%%%%% ARGUMENTS PREPARATION OF BODY GOALS

:- mode normalize_execute_goal_args(+, -, -, ?, +).
normalize_execute_goal_args(G0, G1, B0, B2, N0N1) :-
    functor(G0, F, A), functor(G1, F, A),
    normalize_body_put_args(0, A, G0, G1, B0-B1, B1-B2, N0N1).

/* The instructions to set atomic data including SCNST are generated just
   before 'execute' instruction so that the 'reuse' instruction should be
   generated correctly.   88.12.14 Y.Kimura
*/
:- mode normalize_body_put_args(+, +, +, +, +, +, +).
normalize_body_put_args(A, A, _, _, B0-B0, B1-B1, N-N) :- !.
normalize_body_put_args(K, A, X0, X, B0-B2, B3-B5, N0-N3) :- 
    K1 is K+1, arg(K1, X0, E0), arg(K1, X, E), 
    create_kl1_var(E, N0, N1),
    check_data_if_structure(E0, E, B0, B1, B3, B4, N1-N2),
    normalize_body_put_args(K1, A, X0, X, B1-B2, B4-B5, N2-N3).

:- mode check_data_if_structure(+, +, -, ?, -, ?, +).
check_data_if_structure(E0, E, B0, B1, [E=var(T)|B], B, N0-N2) :- % 890710
    functor(E0,'$LIST',_), !,					  % Nishizaki
    create_kl1_var(T, N0, N1),
    normalize_argument_put(E0, T, B0, B1, N1-N2).
check_data_if_structure(E0, E, B0, B1, [E=var(T)|B], B, N0-N2) :- % 890710
    functor(E0,'$VECT',_), !, 					  % Nishizaki
    create_kl1_var(T, N0, N1),
    normalize_argument_put(E0, T, B0, B1, N1-N2).
check_data_if_structure(E0, E, B, B, B0, B1, N0N1) :- !,
    normalize_argument_put(E0, E, B0, B1, N0N1).

:- mode normalize_body_set_args(+, +, +, -, ?, +).    % 880705 Y.Kimura
normalize_body_set_args(K, A, X0, B0, B1, N0N1) :-
    number_of_argument_slots(Area), 
    A =< Area, !, 
    normalize_body_set_args_1(K, A, X0, B0, B1, N0N1).
normalize_body_set_args(K, A, X0, B0, B3, N0-N4) :-
    number_of_argument_slots(Area), 
    A1 is Area-1,
    normalize_body_set_args_1(K, A1, X0, B0, B1, N0-N1), 
    Arg is A - A1,
    functor(Vect, '$VECT', Arg),
    create_vector_for_exceeded_args(Arg, A, X0, Vect),
    create_kl1_var(V, N1, N2),
    normalize_body_structure_args(0, Arg, Vect, V, 
                                  B2, [Area:=var(V)|B3], [], D, N2-N3),
    normalize_body_builtin(D, B1, [V=vector(Arg)|B2], N3-N4).

:- mode create_vector_for_exceeded_args(+, +, +, +).
create_vector_for_exceeded_args(0, _, _, _) :- !.
create_vector_for_exceeded_args(N, A, X0, Vect) :- 
    arg(A, X0, Arg), arg(N, Vect, Arg),
    N1 is N-1, A1 is A-1,
    create_vector_for_exceeded_args(N1, A1, X0, Vect).

:- mode normalize_body_set_args_1(+, +, +, -, ?, +).
normalize_body_set_args_1(A, A, _, B, B, N-N) :- !.
normalize_body_set_args_1(K, A, X0, B0, B2, N0-N2) :-
    K1 is K+1, arg(K1, X0, E0),
    normalize_argument_set(E0, K1, B0, B1, N0-N1),    
    normalize_body_set_args_1(K1, A, X0, B1, B2, N1-N2).

:- mode normalize_argument_put(+, +, -, ?, +).
normalize_argument_put(E0, E, B0, B1, N0N1) :-
    normalize_active_unify(E0, E, B0, B1, N0N1).

:- mode normalize_argument_set(+, +, -, ?, +).
normalize_argument_set(X, Y, [Y:=var(X)|B], B, N-N) :- kl1_var(X), !.
normalize_argument_set(X, Y, [Y:=atomic(X,T)|B], B, N-N) :- 
    atomic(X), X \== {}, !, kl1_type_of(X,T).
normalize_argument_set(X, Y, B0, B, N0N1) :- 
    functor(X, F, _), normalize_set_structure(F, Y, B0, B, N0N1, X).

:- mode normalize_set_structure(+, +, -, ?, +, +).
normalize_set_structure('$LIST', K, G0, G, N0-N3, X) :- !,
    create_kl1_var(New, N0, N1),
    normalize_body_list_args(X, New, G1, [K:=var(New)|G], [], D, N1-N2),
    normalize_body_builtin(D, G0, [New=list|G1], N2-N3).
normalize_set_structure('$VECT', K, G0, G, N0-N3, X) :- !,
    functor(X, _, A), create_kl1_var(New, N0, N1),
    normalize_body_structure_args(0, A, X, New, 
                                  G1, [K:=var(New)|G], [], D, N1-N2),
    normalize_body_builtin(D, G0, [New=vector(A)|G1], N2-N3).
normalize_set_structure('$SCNST', K, [V0=X,K:=var(V0)|G], G, N0-N1, X) :- !,
    create_kl1_var(V0, N0, N1).
normalize_set_structure(_, K, G0, G, N0-N3, X) :- !,
    create_kl1_var(New, N0, N1),
    normalize_body_structure_args(0, A, X, New, 
                                  G1, [K:=var(New)|G], [], D, N1-N2),
    normalize_body_builtin(D, G0, [New=vector(A)|G1], N2-N3).

%%%%% NORMALIZATION OF ACTIVE UNIFICATION

:- mode normalize_active_unification(+, +, -, ?, +).
normalize_active_unification(X, Y, G0, G, N0N1) :- kl1_var(X), !,
    normalize_active_unify(Y, X, G0, G, N0N1).
normalize_active_unification(Y, X, G0, G, N0N1) :- kl1_var(X), !,
    normalize_active_unify(Y, X, G0, G, N0N1).
normalize_active_unification(X, Y, G0, G, N0N1) :-	
    functor(X, _, A), functor(Y, _, A), !,
    normalize_active_struct_unify(0, A, X, Y, G0, G, N0N1).
normalize_active_unification(X, Y, G, G, N-N) :-
    warn('Active unification always fails: ~w', [X=Y]).

:- mode normalize_active_unify(+, +, -, ?, +).
normalize_active_unify(X, V, [V=var(X)|G], G, N-N) :- kl1_var(X), !.
normalize_active_unify(X, V, [V=atomic(X,T)|G], G, N-N) :- 
    atomic(X), X \== {}, !, kl1_type_of(X, T).
normalize_active_unify(X, V, G0, G, N0N1) :- functor(X, F, _), !,
    normalize_active_structure(F, V, G0, G, N0N1, X).

:- mode normalize_active_struct_unify(+, +, +, +, -, ?, +).    
normalize_active_struct_unify(A, A, X, Y, G, G, N-N) :- !.
normalize_active_struct_unify(I, A, X, Y, G0, G2, N0-N2) :-
    I1 is I+1,
    arg(I1, X, Xe), arg(I1, Y, Ye),
    normalize_structure_element_unify(Xe, Ye, G0, G1, N0-N1),
    normalize_active_struct_unify(I1, A, X, Y, G1, G2, N1-N2).

:- mode normalize_structure_element_unify(?, ?, -, ?, +).
normalize_structure_element_unify(X, Y, G, G, N-N) :-
    atomic(X), atomic(Y), X = Y, !.
normalize_structure_element_unify(X, Y, G, G, N-N) :-
    atomic(X), atomic(Y), !,
    error('Active unification always fails: ~w', [X=Y]).
normalize_structure_element_unify(X, Y, G0, G1, N0N1) :-
    normalize_active_unification(X, Y, G0, G1, N0N1).

:- mode normalize_active_structure(+, +, -, ?, +, +).
normalize_active_structure('$LIST', V0, G0, G, N0-N3, X) :- !,
    create_kl1_var(V, N0, N1),
    normalize_body_list_args(X, V, G1, [V0<=list(V)|G], [], D, N1-N2),
    normalize_body_builtin(D, G0, [V=list|G1], N2-N3).
normalize_active_structure('$VECT', V0, G0, G, N0-N3, X) :- !,
    create_kl1_var(V, N0, N1), functor(X, _, A),
    normalize_body_structure_args(0, A, X, V,
				  G1, [V0<=vector(V)|G], [], D, N1-N2),
    normalize_body_builtin(D, G0, [V=vector(A)|G1], N2-N3).
normalize_active_structure('$SCNST', V, [V0=X,V=var(V0)|G], G, N0-N1, X) :- !,
    create_kl1_var(V0, N0, N1).
normalize_active_structure(_, V0, G0, G, N0-N3, X) :- !,
    create_kl1_var(V, N0, N1), functor(X, _, A),
    normalize_body_structure_args(0, A, X, V,
				  G1, [V0<=vector(V)|G], [], D, N1-N2),
    normalize_body_builtin(D, G0, [V=vector(A)|G1], N2-N3).

:- mode normalize_body_list_args(+, +, -, ?, +, -, +).
normalize_body_list_args(X, V, G0, G2, D0, D, N0-N2) :-
    arg(1, X, Car),
    normalize_body_one_arg(Car, car(V), G0, G1, D0, D1, N0-N1),
    arg(2, X, Cdr),
    normalize_body_one_arg(Cdr, cdr(V), G1, G2, D1, D, N1-N2).

:- mode normalize_body_structure_args(+, +, +, +, -, ?, +, -, +).
normalize_body_structure_args(A, A, _, _, G, G, D, D, N-N) :- !.
normalize_body_structure_args(I, A, X, V, G0, G, D0, D, N0-N2) :-
    I1 is I+1, arg(I1, X, E),
    normalize_body_one_arg(E, vector(V,I), G0, G1, D0, D1, N0-N1),
    normalize_body_structure_args(I1, A, X, V, G1, G, D1, D, N1-N2).

:- mode normalize_body_one_arg(?, +, -, ?, ?, ?, +).
normalize_body_one_arg(X, Attr, [write(var(X),Attr)|G], G, D, D, N0-N1) :- 
    var(X), !, create_kl1_var(X, N0, N1).
normalize_body_one_arg(X, Attr, [write(var(X),Attr)|G], G, D, D, N-N) :- 
    kl1_var(X), !.
normalize_body_one_arg(X, Attr, [write(atomic(X,T),Attr)|G], G, D, D, N-N) :- 
    atomic(X), X \== {}, !, kl1_type_of(X, T).
normalize_body_one_arg(X, Attr, [write(var(V),Attr)|G], G, 
                                                 D,  [V=X|D], N0-N1) :-
    create_kl1_var(V, N0, N1).



