%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% OBJECT LISTING

/********************/
/* Update code list */
/********************/

:- mode update_object_code(+, +, +, -, ?).
update_object_code([], _, _, End, End) :- !.
update_object_code([H|T], From-To-Reg, PC0, Code0, Code1) :- 
    erasable(H, Reg), !, PC is PC0 + 1, 
    update_object_code(T, From-To-Reg, PC, Code0, Code1).
update_object_code([H|T], From-To-Reg, PC0, Code0, Code2) :- 
    update_one_object(H, Reg, Code0, Code1), PC is PC0 + 1, 
    update_object_code(T, From-To-Reg, PC, Code1, Code2).

:- mode erasable(+, +).
erasable(wait_variable(Ai, Aj), Reg) :-
    var_no(Ai, X), var_no(Aj, Y), aref(Reg, X, R), aref(Reg, Y, R), !.
erasable(put_value(Ai, Aj), Reg) :-
    var_no(Ai, X), var_no(Aj, Y), aref(Reg, X, R), aref(Reg, Y, R), !.
erasable(put_value(Ai, Aj), Reg) :-
    var_no(Aj, Y), aref(Reg, Y, 0), !.
erasable(get_list_value(Ai, Aj), Reg) :-
    var_no(Ai, X), var_no(Aj, Y), aref(Reg, X, R), aref(Reg, Y, R), !.
erasable(integer(Ai), Reg) :- 
    var_no(Ai, X), var_type(A, Type), Type == integer, !.
erasable(float(Ai), Reg) :- 		% 890404 Nishizaki
    var_no(Ai, X), var_type(A, Type), Type == float, !.
erasable(commit, _) :- !.

:- mode update_one_object(+, +, -, ?).
update_one_object(calculate(X0), Reg, [calculate(X)|Code], Code) :- !, 
    functor(X0, F, A), functor(X, F, A),
    convert_register_to_real(A, X0, X, Reg).
update_one_object(branch(X0), Reg, [branch(X)|Code], Code) :- !, 
    functor(X0, F, A), functor(X, F, A),		% 890605 Nishizaki
    convert_register_to_real(A, X0, X, Reg).
update_one_object(check(X0, Fail), Reg, [check(X)|Code], Code) :- !,
    convert_register_to_real_with_fail(X0, X, Reg, Fail).
update_one_object(compare(X0, Fail), Reg, [compare(X)|Code], Code) :- !, 
    convert_register_to_real_with_fail(X0, X, Reg, Fail).
update_one_object(wait_variable(Ai, Aj), Reg, Code0, Code1) :- !, 
    update_one_object(put_value(Aj, Ai), Reg, Code0, Code1).
update_one_object(get_marked_value(Ai, Aj), Reg, Code0, Code2) :- !,
    update_one_object(put_marked_value(Ai, Ai), Reg, Code0, Code1),
    update_one_object(get_value(Ai, Aj ), Reg, Code1, Code2).
update_one_object(get_both_marked_value(Ai, Aj), Reg, Code0, Code3) :- !,
    update_one_object(put_marked_value(Ai, Ai), Reg, Code0, Code1),
    update_one_object(put_marked_value(Aj, Aj), Reg, Code1, Code2),
    update_one_object(get_value(Ai, Aj ), Reg, Code2, Code3).
update_one_object(get_list_marked_value(Ai, Aj), Reg, Code0, Code2) :- !,
    update_one_object(put_marked_value(Aj, Aj), Reg, Code0, Code1),
    update_one_object(get_list_value(Ai, Aj), Reg, Code1, Code2).
update_one_object(get_vector_marked_value(Ai, Aj), Reg, Code0, Code2) :- !,
    update_one_object(put_marked_value(Aj, Aj), Reg, Code0, Code1),
    update_one_object(get_vector_value(Ai, Aj), Reg, Code1, Code2).
update_one_object(get_marked_constant(C,Ai), Reg, Code0, Code2) :- !,
    update_one_object(put_marked_value(Ai,Ai), Reg, Code0, Code1),
    update_one_object(get_constant(C,Ai), Reg, Code1, Code2).
update_one_object('$GC_CODE'(Gc), Reg, Code0, Code1) :- !,
    update_object_code(Gc, []-[]-Reg, 0, Code0, Code1).
update_one_object(X, _, [X|Code], Code) :- atomic(X), !.
update_one_object(X0, Reg, [X|Code], Code) :-
    functor(X0, F, A), !, functor(X, F, A),
    convert_register_to_real(A, X0, X, Reg).

:- mode convert_register_to_real_with_fail(+, -, +, ?).
convert_register_to_real_with_fail(X0, X, Reg, Fail) :-
    functor(X0, F, A0), A is A0+1, functor(X, F, A),
    arg(A, X, Fail),
    convert_register_to_real(A0, X0, X, Reg).

:- mode convert_register_to_real(+, +, +, +).
convert_register_to_real(0, _, _, _) :- !. 
convert_register_to_real(A, X0, X, Reg) :- 
    arg(A, X0, E), 
  ( kl1_var(E), !, var_no(E, N), aref(Reg, N, R), arg(A, X, R) ;
    arg(A, X, E) ),
    A1 is A - 1,
    convert_register_to_real(A1, X0, X, Reg).

/*************************/
/*     Output_code/2     */
/*************************/

:- mode output_code(+, +).
output_code(0, Code) :- !,
    output_noindexed_code(Code).
output_code(1, Code) :- !, output_indexed_code(Code).

:- mode output_indexed_code(+).
output_indexed_code([label(F)|Cdr]) :- !,
    write('label('), write_parenthesized(F), write(')'), write('.'), nl,
    output_indexed_code(Cdr).
output_indexed_code([list(X,Fl)|Cdr]) :- !,
    output_indexed_code([wait_list(X,Fl)|Cdr]).
output_indexed_code([Car,Next|Cdr]) :- 
    is_deref_and_type_inst(Car, Next, New), !,
    output_indexed_code([New|Cdr]).
output_indexed_code([Car0|Cdr]) :- 
    unwrap_blt_label(Car0, Car), functor(Car, F, A), !,
    write_one_kl1b(F, A, Car),
    output_indexed_code(Cdr).
output_indexed_code([]) :- !.

:- mode is_deref_and_type_inst(+, +, -).
is_deref_and_type_inst(integer(Ai,Fl),test_constant(C,Ai,Fl), 
                       wait_constant(C,Ai,Fl)) :- !.
is_deref_and_type_inst(float(Ai,Fl),test_constant(C,Ai,Fl), % 890404 Nishizaki
                       wait_constant(C,Ai,Fl)) :- !.
is_deref_and_type_inst(atom(Ai,Fl),test_constant(C,Ai,Fl), 
                       wait_constant(C,Ai,Fl)) :- !.
is_deref_and_type_inst(deref_vector(Ai,Fl),test_arity(C,Ai,Fl), 
                       wait_vector(Ai,C,Fl)) :- !.

:- mode write_one_indexed_code(+).
write_one_indexed_code(One) :- functor(One, F, A),
    write_one_kl1b(F, A, One).

/******************************/
/*   Output_noindexed_code    */
/******************************/

:- mode output_noindexed_code(+).
output_noindexed_code([]) :- !.
output_noindexed_code([label(F)|Cdr]) :- !,
    write('label('), write_parenthesized(F), write(')'), write('.'), nl,
    output_noindexed_code(Cdr).
output_noindexed_code([check(wait(X,Fl)),Next0|Cdr]) :-
    unwrap_blt_label(Next0, Next),
    merge_noindexed_code(Next, X, Fl, New), !, 
    functor(New, F, A), write_one_kl1b(F, A, New),
    output_noindexed_code(Cdr).
output_noindexed_code([Car0|Cdr]) :- unwrap_blt_label(Car0, Car), 
    functor(Car, F, A), !,
    write_one_kl1b(F, A, Car),
    output_noindexed_code(Cdr).

:- mode unwrap_blt_label(+, -).
unwrap_blt_label(check(X), X) :- !.
unwrap_blt_label(compare(X), X) :- !.
unwrap_blt_label(calculate(X), X) :- !.
unwrap_blt_label(branch(X), X) :- !. % 890605 Nishizaki
unwrap_blt_label(X, X) :- !.

:- mode merge_noindexed_code(+, +, +, -).
merge_noindexed_code(integer(X,Fl), X, Fl, integer(X,Fl)) :- !.
merge_noindexed_code(float(X,Fl), X, Fl, float(X,Fl)) :- !. % 890404 Nishizaki
merge_noindexed_code(atom(X,Fl), X, Fl, atom(X,Fl)) :- !.
merge_noindexed_code(list(X,Fl), X, Fl, wait_list(X,Fl)) :- !.
merge_noindexed_code(vector(X,Fl), X, Fl, deref_vector(X,Fl)) :- !. % Nishizaki
merge_noindexed_code(string(X,Fl), X, Fl, wait_string(X,Fl)) :- !.  % Nishizaki

:- mode write_one_kl1b(+, +, +).
write_one_kl1b(F, A, Inst) :- 
    put(9), writeq(F), write_args(A, 1, Inst), write('.'), nl.   

:- mode write_args(+, +, +).
write_args(0, _, _) :- !.
write_args(1, 1, X) :- !, write('('), arg(1, X, Arg), 
    write_one_arg(Arg), write(')').
write_args(A, 1, X) :- !, write('('), arg(1, X, Arg), 
    write_one_arg(Arg), write(','), write_args(A, 2, X).
write_args(A, A, X) :- !, arg(A, X, Arg), 
    write_one_arg(Arg), write(')').
write_args(A, I, X) :- !, arg(I, X, Arg), write_one_arg(Arg), 
    I1 is I+1, write(','), write_args(A, I1, X).

:- mode write_one_arg(?).
write_one_arg(X) :- var(X), !, writeq(X).      % 88.12.26 Y.Kimura
write_one_arg('$SCNST'(T,V)) :- !, 
    write_structured_constant(T, V).
write_one_arg(X) :- write_parenthesized(X).

:- mode write_structured_constant(+, +).
write_structured_constant(string, V) :- !,
    writeq('$SCNST'), write('(string,'), 
    write('"'), write_string(V), write('"'), write(')').
write_structured_constant(ascii, V) :- !,
    writeq('$SCNST'), write('(ascii,'), 
    write('"'), write_string(V), write('"'), write(')').
write_structured_constant(T, V) :- !, writeq('$SCNST'(T,V)).

:- mode write_structured_arg(+, +).
write_structured_arg((module), V) :- !, writeq(V).
write_structured_arg(T, V) :- write('"'), write_string(V), write('"').

:- mode write_string(+).			       
write_string([]) :- !.
write_string([34|X]) :- !, put(34), put(34), write_string(X).
write_string([A|X]) :- put(A), !, write_string(X).

%%%%%%%%%%%%%%%%%%%%%%%%%%%
% output Label/Header/End %
%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- mode output_label(+).
output_label(Label) :- write('label('), 
    write_parenthesized(Label), write(').'), nl.

:- mode output_code_header(+).
output_code_header(F/A) :- write('procedure('), 
    write('('), writeq(F), write(')'),
    write(','), write('('), write(A), write(')).'), nl.

:- mode output_code_end(+).
output_code_end(F/A) :- put(9), write('suspend('), 
    write('('), writeq(F), write(')'),
    write('/'), write('('), write(A), write(')).'), nl, nl.

:- mode write_parenthesized(?).
write_parenthesized(V) :- var(V), !, write(V).    % temporal for indexing
write_parenthesized(F/A/L) :- !,
    write('('), writeq(F), write(')'), write('/'),
    write('('), writeq(A), write(')'), write('/'),
    write('('), writeq(L), write(')').
write_parenthesized(F/A) :- !,
    write('('), writeq(F), write(')'), write('/'),
    write('('), writeq(A), write(')').
write_parenthesized(T) :- atomic(T), !, 
    write('('), writeq(T), write(')').
write_parenthesized(T) :- writeq(T), !.             % For indexing

%%%%% writing module/message information

:- mode output_module_information(?, +).
output_module_information(Module, Ext) :- !,
    nl, write('module_information('), nl, 
    put(9), write(' module('), output_module(Module), write('),'), nl,
    put(9), write(' public('), writeq(Ext), write(')'), nl,
    write(').'), nl, nl.
output_module_information(_, _) :- nl.

:- mode output_module(?).
output_module(Module) :- var(Module), !, 
    warn('module name is not specified... ~n', []),
    writeq([]).
output_module(Module) :- writeq(Module).

:- mode output_term(+).
output_term(X) :- writeq(X), write('.').

:- mode output_term_nl(+).
output_term_nl(X) :- writeq(X), write('.'), nl.

% Help message

klb_help :- !,
    display('tsscomp(0) : compile "user" without MRB instructions.'), ttynl,
    display('tsscomp(1) : compile "user" with MRB maintenance instructions'), 
    ttynl,
    display('		  but without garbage collection instructions.'), 
    ttynl,
    display('tsscomp(2) : compile "user" with MRB full instructions.'),
    ttynl,
    display('kl1compile : file compilation. Optimize level is the same as'),
    ttynl,
    display('		  argument of "tsscomp". This prompts input and'),
    ttynl,
    display('   	  output file name. Input file is Kl1 source'),
    ttynl,
    display('		  program, output file is KLB code file.'), ttynl.

%%%%% GENERATING ERROR/WARNING MESSAGES

:- mode warn(+,+).
warn(Format, Args) :-
    telling(Old), tell(user),
    nl, display('%%% WARNING !! '),
    format(Format, Args),
    nl,
    tell(Old).

:- mode error(+).
error(Format) :- error(Format, []).

:- mode error(+,+).
error(Format, Args) :-
    telling(Old), tell(user),
    nl, display('%%% ERROR !! '),
    format(Format, Args),
    nl,
    tell(Old).
