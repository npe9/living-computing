%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

/**************************

:- op(1150,  fx, (with_macro)).		% Use for user macro reference.
:- op(1150,  fx, (user_macro)).		% Use for user macro library name.
:- op(1150,  fx, (implicit)).		% Use for implicit argument
:- op(1150,  fx, (local_implicit)).	% Use for implicit argument
:- op(1090, xfx, (=>)).			% Use for user macro definition.
:- op( 800, xfx, (:)).			% External Call
:- op( 700, xfx, (:=)).			% Becomes
:- op( 700, xfx, (<=)).			% Use for implicit argument
:- op( 700, xfx, (<<=)).		% Use for implicit argument
:- op( 700, xfy, (@)).			% Pragma
:- op( 700, xfx, ('\=')).		% Not Unifiable
:- op( 500, yfx, (xor)).		% Exclusive OR
:- op( 200,  fx, (&)).			% Use for implicit argument
:- op( 150,  xf, (++)).			% Use for implicit argument
:- op( 150,  xf, (--)).			% Use for implicit argument
:- op( 100, xfx, (#)).			% Sharp Macro
:- op( 100,  fx, (#)).			% Sharp Macro
:- op(  90, xfx, (::)).			% Module Declaration
:- op(  80,  fx, (module)).		% Module Declaration
%% for Floating Point Expression %% 890404 Nishizaki
:- op( 700, xfx, ($:=)).		% Becomes
:- op( 700, xfx, ($<=)).		% Implicit Argument
:- op( 700, xfx, ($=:=)).		% Equal
:- op( 700, xfx, ($=\=)).		% Not Equal
:- op( 700, xfx, ($<)).			% Less Than
:- op( 700, xfx, ($>=)).		% Not Less Than
:- op( 700, xfx, ($>)).			% Greater Than
:- op( 700, xfx, ($=<)).		% Not Greater Than
:- op( 300, xfy, (**)).			% Power

:- public test/2.
test(In,Out) :-
    recorda('$$$new_unique_number_for_case_expansion', 0, _), 
    clear_implicit_args,
    see(In), tell(Out),
    read(Cls),
    read_declaration(Cls, Cls1), nl,
    loop(Cls1).

loop(end_of_file) :- !, seen, told.
loop(Cls) :- 
    translate_clause(Cls, NewCls, Cases),
    write_cls_(NewCls),
    write_clss(Cases),
    read(Cls1),
    loop(Cls1).


read_declaration(end_of_file, end_of_file) :- !.
read_declaration((:- module Args), Cls) :- !,
    write_cls((:- module Args)),
    read(Cls1), read_declaration(Cls1, Cls).
read_declaration((:- public Args), Cls) :- !,
    write_cls((:- public Args)),
    read(Cls1), read_declaration(Cls1, Cls).
read_declaration((:- implicit Args), Cls) :- !,
    check_declaration_of_implicit_args(Args, H,T),
    replace_implicit_arg_template(global_implicit_args, H,T),
    write_cls((:- implicit Args)),
    read(Cls1), read_declaration(Cls1, Cls).
read_declaration((:- local_implicit), Cls) :- !,
    replace_implicit_arg_template(local_implicit_args, H,H),
    write_cls((:- local_implicit)),
    read(Cls1), read_declaration(Cls1, Cls).
read_declaration((:- local_implicit Args), Cls) :- !,
    check_declaration_of_implicit_args(Args, H,T),
    replace_implicit_arg_template(local_implicit_args, H,T),
    write_cls((:- local_implicit Args)),
    read(Cls1), read_declaration(Cls1, Cls).
read_declaration((:- op(X,Y,Z)), Cls) :- !,
    call(op(X,Y,Z)), write_cls((:- op(X,Y,Z))),
    read(Cls1), read_declaration(Cls1, Cls).
read_declaration(Cls, Cls).

:- mode error(+).
error(Format) :- error(Format, []).

:- mode error(+,+).
error(Format, Args) :-
    telling(Old), tell(user),
    nl, display('%%% ERROR !! '),
    format(Format, Args),
    nl,
    tell(Old).

write_clss([]) :- !.
write_clss([X|Y]) :- write_cls_(X), write_clss(Y).

write_cls_(X) :- numbervars(X, 0, _), write_cls(X), fail.
write_cls_(_).

	write_cls((:- X)) :- !,
    write(' :- '), write(X), put("."), nl.
write_cls((H:-G|B)) :- !,
    write(H), write(' :- '), nl,
    tab(2), write(G), write(' |'), nl,
    write_goals(B, end).
write_cls(X) :- write(X), put("."), nl, nl.

write_goals((A,B), _) :- !, write_goals(A, no), write_goals(B, end).
write_goals(A, no) :- tab(4), write(A), put(","), nl.
write_goals(A, end) :- tab(4), write(A), put("."), nl, nl.

***************************/

/**************************** for DEC10-Prolog
copy_term(X,Y) :- var(X), !, X=Y.
copy_term(X,Y) :- atomic(X), !, X=Y.
copy_term(X,Y) :- 
    functor(X,F,A), functor(Y,F,A),
    copy_fnc_args(A, X, Y).

copy_fnc_args(0, _, _) :- !.
copy_fnc_args(K, X, Y) :-
    K1 is K-1,
    arg(K, X, Xk), arg(K, Y, Yk), copy_term(Xk, Yk),
    copy_fnc_args(K1, X, Y).
****************************/

:- public translate_clause/4.
translate_clause(( :- local_implicit), ( :- local_implicit), [], Ex-Ex) :- !,
    replace_implicit_arg_template(local_implicit_args, H,H).
translate_clause(( :- local_implicit A), ( :- local_implicit A), [], Ex-Ex) :- !,
    check_declaration_of_implicit_args(A, H,T),
    replace_implicit_arg_template(local_implicit_args, H,T).
translate_clause(( :- implicit A), ( :- implicit A ), [], Ex-Ex) :- !,
    exerror('Declaration of global implicit argument must be placed at beginning of module.',[]).
translate_clause(( :- op(Prec,Type,Op)), ( :- op(Prec,Type,Op)), [], Ex-Ex) :- 
    !, call(op(Prec,Type,Op)).
translate_clause(( :- A ), ( :- A ), [], Ex-Ex) :- !.
translate_clause(otherwise, otherwise, [], Ex-Ex) :- !.
translate_clause(alternatively, alternatively, [], Ex-Ex) :- !.
translate_clause(end_of_file, end_of_file, [], Ex-Ex) :- !.
translate_clause(Cls, NewCls, Cases, EX) :-
    translate_one_clause_(Cls, NewCls, Cases, EX), !.

translate_one_clause_((H:-G|B), NewCls, Cases, Ex-Ex1) :- G \== (_->_), !,
    functor(H, F, A),
    case_expansion(B, B1, H+G, F/A, no_imp, Cases1, []),
    translate_one_clause((H:-G|B1), NewCls, Ex-Ex0),
    translate_clss(Cases1, Cases, Ex0-Ex1).
translate_one_clause_((H-->G|B), NewCls, Cases, Ex-Ex1) :- G \== (_->_), !,
    functor(H, F, A),
    case_expansion(B, B1, H+G, F/A, imp, Cases1, []),
    translate_one_clause((H-->G|B1), NewCls, Ex-Ex0),
    translate_clss(Cases1, Cases, Ex0-Ex1).
translate_one_clause_((H:-B), NewCls, Cases, EX) :- !,
    translate_one_clause_((H:-true|B), NewCls, Cases, EX).
translate_one_clause_((H-->B), NewCls, Cases, EX) :- !,
    translate_one_clause_((H-->true|B), NewCls, Cases, EX).
translate_one_clause_((H), NewCls, Cases, EX) :- !,            % 880809 Y.K
    translate_one_clause_((H:-true|true), NewCls, Cases, EX).

translate_clss([], [], Ex-Ex) :- !.
translate_clss([C|Cs], [Nc|Ncs], Ex-Ex1) :-
    translate_one_clause(C, Nc, Ex-Ex0),
    translate_clss(Cs, Ncs, Ex0-Ex1).

%:- mode translate_one_clause(+, -, +).
translate_one_clause(Cls, Cls1, Ex-Ex) :- recorded(macro_expander,off,_), !,
    translate_one_clause_(Cls, Cls1).
translate_one_clause((H:-G|B), (H1:-Guard|Body), Ex-Ex1) :- !,
    translate_head(H,H1, Gg1, [],Dict1, no_expand),
    translate_goals(G,G1, Dict1,Dict2, no_expand,guard, Ex-Ex0),
    translate_goals(B,B1, Dict2,Dict3, no_expand,body, Ex0-Ex1),
%    opt_true((Gg1,G1), Guard), opt_true(B1, Body).
    opt_true_unify((Gg1,G1), Guard), opt_true(B1, Body).   % 880721 Y.Kimura
translate_one_clause((H:-B), Cls, EX) :- !,
    translate_one_clause((H:-true|B), Cls, EX).
translate_one_clause((H-->G|B), (H1:-Guard|Body), Ex-Ex1) :- !,
    make_dict(Dict),
    translate_head(H,H1, Gg1, Dict,Dict1, expand),
    translate_goals(G,G1, Dict1,Dict2, no_expand,guard, Ex-Ex0),
    translate_goals(B,B1, Dict2,Dict3, expand,body, Ex0-Ex1),
    translate_finalize(Dict3, B1,Bb1),
%    opt_true((Gg1,G1), Guard), opt_true(Bb1, Body).
    opt_true_unify((Gg1,G1), Guard), opt_true(Bb1, Body).  % 880721 Y.Kimura
translate_one_clause((H-->B), Cls, EX) :- !,
    translate_one_clause((H-->true|B), Cls, EX).
translate_one_clause(otherwise, otherwise, Ex-Ex) :- !.
translate_one_clause(alternatively, alternatively, Ex-Ex) :- !.
translate_one_clause( H, Cls, EX) :-
    translate_one_clause((H:-true|true), Cls, EX).

translate_one_clause_(( :- A ), ( :- A )) :- !.
translate_one_clause_((H-->G|B), Cls) :- G = (_->_), !,
    translate_one_clause_((H-->true|(G;B)), Cls).
translate_one_clause_((H-->G|B), (H1:-G|B1)) :- C1 = (_->_), !,
    translate_dcg_left(H,H1,S0,S), translate_dcg(B,B1,S0,S).
translate_one_clause_((H:-G|B), (H:-true|(G;B))) :- G = (_->_), !.
translate_one_clause_((H:-G|B), (H:-G|B)) :- !.
translate_one_clause_((H:-B), (H:-true|B)) :- !.
translate_one_clause_((H-->G|B), (H1:-G|B1)) :- !,
    translate_dcg_left(H,H1,S0,S), translate_dcg(B,B1,S0,S).
translate_one_clause_( H, Cls) :-
    translate_one_clause_((H:-true|true), Cls).

translate_case_goals((C1;C2),((G1->Bgs);NG), Dict1, SW) :-
    C1 = (G->B), !,
    translate_goals(G,G1, Dict1,Dict2, SW, body),
    translate_goals(B,B1, Dict2,Dict3, SW, body),
    translate_finalize(Dict3, B1,Bgs),
    translate_case_goals(C2,NG, Dict1, SW).

check_declaration_of_implicit_args(X, H, T) :- nonvar(X),
    check_declaration_of_implicit_args_(X, H, T),
    not_duplicated(H), !.
check_declaration_of_implicit_args(X, T, T) :-
    exerror('Implicit argument declaration was wrong. ~n',[]).

check_declaration_of_implicit_args_(Name:Type, [(Name,Type)|T], T) :-
    atom(Name), atom(Type),
    arg_name_not_duplicated(Name),
    check_declaration_of_implicit_type(Type), !.
check_declaration_of_implicit_args_((X,Y), H,T) :- !,
    check_declaration_of_implicit_args_(X, H,M), !,
    check_declaration_of_implicit_args_(Y, M,T).
check_declaration_of_implicit_args_(X, H,H) :- !,
    exerror('Implicit argument declaration was wrong. ~n~w',[X]).

%:- mode check_declaration_of_implicit_type(+).
check_declaration_of_implicit_type(oldnew) :- !.
check_declaration_of_implicit_type(stream) :- !.
check_declaration_of_implicit_type(string) :- !.
check_declaration_of_implicit_type(shared).

replace_implicit_arg_template(global_implicit_args,H,T) :- var(H), !.
replace_implicit_arg_template(Key,_,_) :- recorded(Key,_,Id), erase(Id), fail.
replace_implicit_arg_template(local_implicit_args,H,T) :- 
    var(H), !, recorda(local_implicit_args, (X,X), _).
replace_implicit_arg_template(Key,H,T) :- recorda(Key, (H,T), _).

%:- mode oldnew(+).
oldnew(oldnew) :- !.  oldnew(string) :- !.

%:- mode translate_finalize(+, +, -).
translate_finalize([], Ng,Ng) :- !.
translate_finalize([$(_,shared,_)|D], Ng1,Ng2) :- !,
    translate_finalize(D, Ng1,Ng2).
translate_finalize([$(_,stream,List)|D], Ng1,Ng3) :- !,
  ( var(List), !, MergeIn = (List=[]), Ng3 = (MergeIn,Ng2) ;
    make_merge_in(List, on, Vect, SS), !,
        Vect1 =.. [{},Vect], Ng3 = ((SS=Vect1),Ng2) ;
    List = (X,X), Ng3 = Ng2 ),
    translate_finalize(D, Ng1,Ng2).
translate_finalize([$(_,Type,Xh-Xt,_)|D], Ng1,Ng3) :- !, 
    Ng2 = ((Xh=Xt),Ng1),
    translate_finalize(D, Ng2,Ng3).
/*********
translate_finalize([$(_,Type,X-X,yes)|D], Ng1,Ng2) :- !, 
    translate_finalize(D, Ng1,Ng2).
translate_finalize([$(_,Type,Xh-Xt,no)|D], Ng1,Ng3) :- !, 
    Ng2 = ((Xh=Xt),Ng1),
    translate_finalize(D, Ng2,Ng3).
*********/

make_merge_in((A,B), on, _, _) :- var(A), var(B), !, fail.
make_merge_in((A,BB), _, (A,D), T) :- nonvar(BB), !,
    make_merge_in(BB, off, D, T).
make_merge_in((A,B), _, A, B).

%%% translate_goals(SW, Gs,TGs, Ng1,Ng2, N, Dict,NewDict, Position,Extra)
%:- mode translate_goals(+,-,+,-,+,+,+).
translate_goals(X,X, Id,Id, _,guard,Ex-Ex) :- var(X), !,
    error('Guard goal not implemented: ~w', [X]).
translate_goals(X,X, Id,Id, _,body,Ex-Ex) :- var(X), !,
    error('Body goal not implemented: ~w', [X]).
translate_goals(true,true, Id,Id, _,_,Ex-Ex) :- !.
translate_goals((X,Y),(X1,Y1), Id1,Id3, SW,Position, Ex-Ex1) :- !,
    translate_goals(X,X1, Id1,Id2, SW,Position, Ex-Ex0),
    translate_goals(Y,Y1, Id2,Id3, SW,Position, Ex0-Ex1).
translate_goals({{Gs}},Gs1, Id1,Id2, _,body, EX) :- !,
    translate_goals(Gs,Gs1, Id1,Id2, no_expand,body, EX).
translate_goals((Module:Goal@Pragma), Ng, Id1,Id3, SW,body, Ex-Ex1) :- !,
    translate_goal(Goal,Goal1, Id1,Id2, SW,body),
    split_original_goal(Goal1, Pre, OG),
    make_external_goal(Module, OG, ExGoal, Ex-Ex0),
    translate_goals((Pre,ExGoal@Pragma), Ng, Id2,Id3, no_expand,body, Ex0-Ex1).
translate_goals((Goal@Pragma1@Pragma2), Ng, Id1,Id4, SW,body, Ex-Ex1) :- !,
    translate_goal(Goal,Goal1, Id1,Id2, SW,body),
    split_original_goal(Goal1, Pre, OG),
    expand_term(Pragma2,Pragma22, true,PNg, Id2,Id3, body),
    make_pragma_goal(Pragma22, OG, ExGoal, 0, Ex-Ex0),
    translate_goals((Pre,PNg,ExGoal@Pragma1), Ng, Id3,Id4, no_expand,body, Ex0-Ex1).
translate_goals((Module:Goal),(Pre,Module:OG), Id1,Id2, SW,body, Ex-Ex) :- !,
    translate_goal(Goal,Goal1, Id1,Id2, SW,body),
    split_original_goal(Goal1, Pre, OG).
translate_goals((Goal@Pragma), Ng, Id1,Id3, SW,body, Ex-Ex) :- !,
    translate_goal(Goal,Goal1, Id1,Id2, SW,body),
    split_original_goal(Goal1, Pre, OG),
    expand_term(Pragma,Pragma1, (Pre,OG@Pragma1),Ng, Id2,Id3, body).
translate_goals(Goal,Goal1, Id1,Id2, SW,Pos, Ex-Ex) :-
    translate_goal(Goal,Goal1, Id1,Id2, SW,Pos).

split_original_goal(Goal, true, Goal) :- var(Goal), !.
split_original_goal((Pre1,OG1), (Pre1,Pre), OG) :- !,
	split_original_goal(OG1, Pre, OG).
split_original_goal(Goal, true, Goal) :- !.

make_external_goal(Module, Goal, ExGoal, []-[(Module:F/A,ExP)]) :- !,
    Goal =.. [F|Args], length(Args,A),
    name(Module,ML), name(F,FL), name(A,AL),
    append_list(["$",ML,":",FL,"/",AL],PL),
    name(ExP,PL),
    ExGoal =.. [ExP|Args].
make_external_goal(Module, Goal, ExGoal, Ex-Ex) :-
	Ex = [(Module:F/A,ExP)|_], Goal =.. [F|Args], length(Args,A), !,
    ExGoal =.. [ExP|Args].
make_external_goal(Module, Goal, ExGoal, [OneEx|Ex]-[OneEx|Ex1]) :- !,
    make_external_goal(Module, Goal, ExGoal, Ex-Ex1).

make_pragma_goal(Pragma, Goal, ExGoal, UN, []-[(F/A@Pragma,ExP,UN)]) :- !,
    Goal =.. [F|Args], length(Args,A),
    functor(Pragma,PG,_), name(PG,PGL), name(F,FL), name(A,AL), name(UN,UNL),
    append_list(["$",FL,"/",AL,"@",PGL,UNL],PL),
    name(ExP,PL),
    Pragma =.. [PF|PArgs], append(Args,PArgs,ExArgs),
    ExGoal =.. [ExP|ExArgs].
make_pragma_goal(Pragma, Goal, ExGoal, _, Ex-Ex) :-
	Goal =.. [F|Args], length(Args,A),
	Ex = [(F/A@Pragma0,ExP,UN)|_], Pragma == Pragma0, !,
    ExGoal =.. [ExP|Args].
make_pragma_goal(Pragma, Goal, ExGoal, _, [OneEx|Ex]-[OneEx|Ex1]) :-
    OneEx = (_,_,UN), !,
    UN1 is UN + 1,
    make_pragma_goal(Pragma, Goal, ExGoal, UN1, Ex-Ex1).
make_pragma_goal(Pragma, Goal, ExGoal, UN, [OneEx|Ex]-[OneEx|Ex1]) :- !,
    make_pragma_goal(Pragma, Goal, ExGoal, UN, Ex-Ex1).

append_list([One|T],L) :- append(One,TT,L), append_list(T,TT).
append_list([],[]).

%:- mode translate_goal(+,-,+,-,+,+).
translate_goal(G,G, Id,Id, _,_) :- var(G), !.
translate_goal(&X,G, Id1,Id2, _,_) :-
    X =..[Op,ArgName], what_fnc_unary(Op,Fnc), !,
    find_implicit_elem(Id1, ArgName, Type, Value),
  ( (Type==shared ; Type==oldnew), !,
       translate_implicit_goal_unary(Fnc, ArgName, Value, G, Id1, Id2, Type) ;
    exerror('Illegal expression of implicit argument. ~n~w', [&X]) ).
translate_goal(&G,true, Id,Id, _,_) :- !,
    exerror('Implicit arg can not write at goal level. ~n~w',[&G]).
/*
translate_goal((A := B),Ng, Id1,Id3, _,body) :- !,
    expand_term(A, A1, Ng0,Ng1, Id1,Id2, body),
    expand_term_(B, B1, Ng1,Ng, Id2,Id3, body),
    Ng0 = (A1=B1).
*/
translate_goal((A := B),Ng, Id1,Id3, _,body) :- !,
    expand_term(A, A1, true,Ng0, Id1,Id2, body),
    expand_term_(B, B1, Ng0,Ng1, Id2,Id3, body),
    Ng = (Ng1,(A1=B1)).
translate_goal((A := B),Ng, Id1,Id3, _,Position) :- !,
    expand_term(A, A1, Ng0,Ng1, Id1,Id2, Position),
    expand_term_(B, B1, Ng1,Ng, Id2,Id3, Position),
  ( B==B1, !, Ng0 = (A1=B1) ;
    expand_assign(A1, B1), ! ;
    exerror('No arithmetic expression. ~n~w',[A:=B]) ), !.
/*
translate_goal((A := B),Ng, Id1,Id3, _, Position) :- !,
    expand_term(A, A1, true,Ng1, Id1,Id2, Position),
    expand_term_(B, B1, Ng1,Ng, Id2,Id3, Position),
  ( expand_assign(A1, B1), ! ;
    exerror('No arithmetic expression. ~n~w',[A:=B]) ).
*/
translate_goal((A $:= B),Ng, Id1,Id3, _,body) :- !,
    expand_term(A, A1, true,Ng0, Id1,Id2, body),
    expand_float_term_(B, B1, Ng0,Ng1, Id2,Id3, body),
    Ng = (Ng1,(A1=B1)).
translate_goal((A $:= B),Ng, Id1,Id3, _,Position) :- !,
    expand_term(A, A1, Ng0,Ng1, Id1,Id2, Position),
    expand_float_term_(B, B1, Ng1,Ng, Id2,Id3, Position),
  ( B==B1, !, Ng0 = (A1=B1) ;
    expand_float_assign(A1, B1), ! ;
    exerror('No arithmetic expression. ~n~w',[A$:=B]) ), !.
translate_goal((A <= B),Ng, Id1,Id3, _,Position) :- !,
    expand_term_(B, NewB, true,Ng0, Id1,Id2, Pos),
    translate_implicit_goal(A,NewB, Gs, Ng0,Ng1, Id2,Id3, Position, set),
    Ng = (Ng1,Gs).
translate_goal((A $<= B),Ng, Id1,Id3, _,Position) :- !,
    expand_float_term_(B, NewB, true,Ng0, Id1,Id2, Pos),
    translate_implicit_goal(A,NewB, Gs, Ng0,Ng1, Id2,Id3, Position, set),
    Ng = (Ng1,Gs).
translate_goal((A <<= B),Ng, Id1,Id3, _,Position) :- !,
    expand_term(B, NewB, true,Ng0, Id1,Id2, Pos),
    translate_implicit_goal(A,NewB, Gs, Ng0,Ng1, Id2,Id3, Position, dcg),
    Ng = (Ng1,Gs).

translate_goal(C#G,(Ng,Gs), Id1,Id2, no_expand,guard) :- atomic(C), !,
    functor(G,F,A),
    expand_arg_elem(0,A, G,Args,[], true,Ng, Id1,Id2, guard),
    GG =.. [F|Args],
    expand_sharp_macro(C#GG, Gs).
translate_goal(C#G,Ng, Id1,Id2, no_expand,Position) :- atomic(C), !,
    functor(G,F,A),
    expand_arg_elem(0,A, G,Args,[], Gs,Ng, Id1,Id2, Position),
    GG =.. [F|Args],
    expand_sharp_macro(C#GG, Gs).
translate_goal(C#G,Ng, Id1,Id2, expand,body) :- atomic(C),
    functor(G, Fnc, Nargs), body_blt(Fnc, Nargs, _, _, _, _), !,
    expand_arg_elem(0,Nargs, G,Args,[], Gs,Ng, Id1,Id2, body),
    GG=..[Fnc|Args],
    expand_sharp_macro(C#GG, Gs).
translate_goal(C#G,(Ng,Gs), Id1,Id3, expand,guard) :- atomic(C), !,
    functor(G,F,A),
    get_implicit_args(Args,ArgsT, Id1,Id2),
    expand_arg_elem(0,A, G,ArgsT,[], true,Ng, Id2,Id3, guard),
    GG =.. [F|Args],
    expand_sharp_macro(C#GG, Gs).
translate_goal(C#G,Ng, Id1,Id3, expand,Position) :- atomic(C), !,
    functor(G,F,A),
    get_implicit_args(Args,ArgsT, Id1,Id2),
    expand_arg_elem(0,A, G,ArgsT,[], Gs,Ng, Id2,Id3, Position),
    GG =.. [F|Args],
    expand_sharp_macro(C#GG, Gs).

translate_goal(floating_point(A),Ng, Id1,Id2, SW,guard) :- !,
    translate_goal(float(A),Ng, Id1,Id2, SW,guard).
translate_goal(merge(A,B,C),Ng, Id1,Id2, SW,body) :- !,
    translate_goal(merge({A,B},C),Ng, Id1,Id2, SW,body).
translate_goal(merge_in(A,B,C),Ng, Id1,Id2, SW,body) :- !,
    translate_goal((C={A,B}),Ng, Id1,Id2, SW,body).

translate_goal(G,(Ng,Gs), Id1,Id2, no_expand,guard) :-
    expand_binary_op(G, Gs, true,Ng, Id1,Id2, guard), !.
translate_goal(G,(Ng,Gs), Id1,Id2, no_expand,Position) :- !,
    functor(G,F,A),
    expand_arg_elem(0,A, G,Args,[], true,Ng, Id1,Id2, Position),
    Gs =.. [F|Args].
/* 890511 Nishizaki
translate_goal(G,(Ng,Gs), Id1,Id2, no_expand,guard) :- !,
    functor(G,F,A),
    expand_arg_elem(0,A, G,Args,[], true,Ng, Id1,Id2, guard),
    Gs =.. [F|Args].
translate_goal(G,Ng, Id1,Id2, no_expand,Position) :- !,
    functor(G,F,A),
    expand_arg_elem(0,A, G,Args,[], Gs,Ng, Id1,Id2, Position),
    Gs =.. [F|Args].
*/
translate_goal(G,(Ng,Gs), Id1,Id2, expand,body) :- 
    functor(G, Fnc, Nargs), body_blt(Fnc, Nargs, _, _, _, _), !,
    expand_arg_elem(0,Nargs, G,Args,[], true,Ng, Id1,Id2, body),
    Gs=..[Fnc|Args].
/* 890922 Nishizaki
translate_goal(G,Ng, Id1,Id2, expand,body) :- 
    functor(G, Fnc, Nargs), body_blt(Fnc, Nargs, _, _, _, _), !,
    expand_arg_elem(0,Nargs, G,Args,[], Gs,Ng, Id1,Id2, body),
    Gs=..[Fnc|Args].
*/
translate_goal(G,(Ng,Gs), Id1,Id3, expand,guard) :- !,
    functor(G,F,A),
    get_implicit_args(Args,ArgsT, Id1,Id2),
    expand_arg_elem(0,A, G,ArgsT,[], true,Ng, Id2,Id3, guard),
    Gs =.. [F|Args].
%translate_goal(G,(Ng,Gs), Id1,Id3, expand,Position) :-
%    functor(G,F,A),
%    get_implicit_args(Args,ArgsT, Id1,Id2),
%    expand_arg_elem(0,A, G,ArgsT,[], true,Ng, Id2,Id3, Position),
%    Gs =.. [F|Args].
translate_goal(G,(Ng,Gs), Id1,Id3, expand,Position) :-
    functor(G,F,A),
    expand_arg_elem(0,A, G,ArgsT,[], true,Ng, Id1,Id2, Position),
    get_implicit_args(Args,ArgsT, Id2,Id3),
    Gs =.. [F|Args].
/* 890922 Nishizaki
translate_goal(G,Ng, Id1,Id3, expand,Position) :-
    functor(G,F,A),
    get_implicit_args(Args,ArgsT, Id1,Id2),
    expand_arg_elem(0,A, G,ArgsT,[], Gs,Ng, Id2,Id3, Position),
    Gs =.. [F|Args].
*/

translate_head(G,Gs, Ng, Id1,Id2, no_expand) :- !,
    functor(G,F,A),
    expand_arg_elem(0,A, G,Args,[], true,Ng, Id1,Id2, head),
    Gs =.. [F|Args].
translate_head(G,Gs, Ng, Id1,Id2, expand) :-
    functor(G,F,A),
    get_implicit_args_(Args,ArgsT, Id1),
    expand_arg_elem(0,A, G,ArgsT,[], true,Ng, Id1,Id2, head),
    Gs=..[F|Args].

translate_implicit_goal_unary(Fnc, ArgName, Value, G, Id1,Id2, shared) :- !,
    replace_i_dict(ArgName,NewValue, Id1,Id2),
    G=..[Fnc,Value,NewValue], !.
translate_implicit_goal_unary(Fnc, ArgName, H-T, G, Id1,Id2, oldnew) :-
    replace_i_dict(ArgName,(NewValue-T), Id1,Id2),
    G=..[Fnc,H,NewValue], !.

what_fnc_unary((++), increment) :- !.
what_fnc_unary((--), decrement) :- !.

translate_implicit_goal(A,B, true, Ng,Ng, Id,Id, Position, Type) :- var(A), !,
  ( Type==dcg, !, exerror('Illegal expression. ~n~w',[A <<= B]) ;
    exerror('Illegal expression. ~n~w',[A <= B]) ).
translate_implicit_goal(&X,B, Gs, Ng1,Ng2, Id1,Id2, Position, Type) :-
    X=..[ArgName,N], atom(ArgName),
    !, expand_implicit_arg(ArgName,B, Gs, Ng1,Ng2, Id1,Id2,Position,$(Type,N)).
translate_implicit_goal(&ArgName,B, Gs, Ng1,Ng2, Id1,Id2, Position, Type) :-
    atom(ArgName),
    !, expand_implicit_arg(ArgName,B, Gs, Ng1,Ng2,Id1,Id2,Position,$(Type,no)).
translate_implicit_goal(A,B, true, Ng,Ng, Id,Id, Position, Type) :-
  ( Type==dcg, !, exerror('Illegal expression. ~n~w',[A <<= B]) ;
    exerror('Illegal expression:: ~w',[A <= B]) ).

%:- mode expand_implicit_arg(+,?,-,+,-,+,-,+,+).
expand_implicit_arg(ArgName,Right, Gs, Ng1,Ng2, Id1,Id2, Pos, Op) :- 
    find_implicit_elem(Id1, ArgName, Type, Value), !,
    trans_implicit_(Type,ArgName,Value, Right,Gs,Ng1,Ng2,Id1,Id2, Pos, Op).
expand_implicit_arg(ArgName,_, true, Ng,Ng, Id,Id, _, _) :- 
    exerror('Implicit argument (~w) is not defined.',[ArgName]).

%:- mode trans_implicit_(+,+,?,?,-,+,-,+,-,+,+).
trans_implicit_(shared,ArgName,_, Right,true,Ng,Ng,Id1,Id2,Pos,$(set,N)) :- 
    N==no, !,
    replace_i_dict(ArgName,Right, Id1,Id2).
trans_implicit_(shared,ArgName,Value,Right,Gs,Ng1,Ng2,Id1,Id3,Pos,$(set,N)) :- 
    Gs = set_vector_element(Value,NewN,_,Right,NewValue),
    expand_term(N, NewN, Ng1,Ng2, Id1,Id2, Pos),
    replace_i_dict(ArgName,NewValue, Id2,Id3).
trans_implicit_(stream,ArgName,Value,Right,Gs,Ng,Ng,Id1,Id2,Pos,$(dcg,N)):-
    N==no, !,
  ( Right == [], !, Gs = true, Id1=Id2 ;
    trans_dcg_right(Right, NewRight, Cdr),
      ( var(Value), !, Gs=(Value=NewRight),
            replace_i_dict(ArgName,Cdr, Id1,Id2) ;
        get_stream_tail(Value, Tail, Cdr, NewValue), Gs = (Tail=NewRight),
            replace_i_dict(ArgName,NewValue, Id1,Id2) ) ).
trans_implicit_(oldnew,ArgName,_-T,Right,true,Ng,Ng,Id1,Id2,Pos,$(set,N)):-
    N==no, !,
    replace_i_dict(ArgName,(Right-T), Id1,Id2).
trans_implicit_(oldnew,ArgName,H-T,Right,Gs,Ng,Ng,Id1,Id2,Pos,$(dcg,N)) :-
    N==no, !,
    Gs = (H=NewRight),
    trans_dcg_right(Right, NewRight, NewH),
    replace_i_dict(ArgName,(NewH-T), Id1,Id2).
trans_implicit_(oldnew,ArgName,H-T,Right,Gs,Ng1,Ng2,Id1,Id3,Pos,$(dcg,N)):- !,
    Gs = set_vector_element(H,NewN,NewRight,NewCdr,NewH),
    expand_term(N, NewN, Ng1,Ng2, Id1,Id2, Pos),
    trans_dcg_right(Right, NewRight, NewCdr),
    replace_i_dict(ArgName,(NewH-T), Id2,Id3).
trans_implicit_(oldnew,ArgName,H-T,Right,Gs,Ng1,Ng2,Id1,Id3,Pos,$(set,N)) :- !,
    Gs = set_vector_element(H,NewN,_,Right,NewH),
    expand_term(N, NewN, Ng1,Ng2, Id1,Id2, Pos),
    replace_i_dict(ArgName,(NewH-T), Id2,Id3).
trans_implicit_(string,ArgName,H-T,Right,Gs,Ng1,Ng2,Id1,Id3,Pos,$(set,N)) :- !,
    Gs = set_string_element(H,NewN,Right,NewH),
    expand_term(N, NewN, Ng1,Ng2, Id1,Id2, Pos),
    replace_i_dict(ArgName,(NewH-T), Id2,Id3).
trans_implicit_(_,ArgName,_,_, true, Ng,Ng, Id,Id,_,_) :- 
    exerror('Illegal expression. ~n~w', [ArgName]).

get_stream_tail(Tail, Tail, Cdr, Cdr) :- var(Tail), !.
get_stream_tail((X,Y), Tail, Cdr, (X,YY)) :-
    get_stream_tail(Y, Tail, Cdr, YY).

%:- mode trans_dcg_right(?,?,?).
trans_dcg_right(X, NewCdr, NewCdr) :- var(X), !,
    exerror('Type error for implicit argument.',[]).
%trans_dcg_right(X, NewCdr, X) :- var(X), !.
trans_dcg_right([], NewCdr, NewCdr) :- !.
trans_dcg_right([Car|Cdr], [Car|NewCdr], NewTail) :- !,
    trans_dcg_right(Cdr, NewCdr, NewTail).
trans_dcg_right(_, NewCdr, NewCdr) :- 
    exerror('Type error for implicit argument.',[]).

%%%%%%%%
%:- mode find_implicit_elem(+,+,-,?).
find_implicit_elem([$(Name,Type,Value)|_], Name, Type, Value) :- !.
find_implicit_elem([$(Name,Type,Value,_)|_], Name, Type, Value) :- !.
find_implicit_elem([_|Id], Name, Type, Value) :- !,
    find_implicit_elem(Id, Name, Type, Value).
find_implicit_elem([], Name, _, _) :- !,
    exerror('~w was not defined as implicit argument.',[Name]), fail.

%:- mode replace_i_dict(+,?,+,-).
replace_i_dict(Name,Value, [$(Name,Type,_)|Id],[$(Name,Type,Value)|Id]) :- !.
replace_i_dict(Name,Value, [$(Name,Type,_,SW)|Id],[$(Name,Type,Value,yes)|Id]) :- !.
replace_i_dict(Name,Value, [$(N,T,V)|Id1],[$(N,T,V)|Id2]) :- !,
    replace_i_dict(Name, Value, Id1, Id2).
replace_i_dict(Name,Value, [$(N,T,V,SW)|Id1],[$(N,T,V,SW)|Id2]) :-
    replace_i_dict(Name, Value, Id1, Id2).

%:- mode get_implicit_args(-,?,+,-).
get_implicit_args(T,T, [], []) :- !.
get_implicit_args([Vh,Vm|Ah],At,[$(N,Type,Vh-Vt,_)|I],[$(N,Type,Vm-Vt,yes)|II]) :- 
    oldnew(Type), !, get_implicit_args(Ah,At, I, II).
get_implicit_args([VV|Ah],At,[$(N,stream,V)|I],[$(N,stream,(VV,V))|II]) :- !,
    get_implicit_args(Ah,At, I, II).
get_implicit_args([V|Ah],At, [$(N,shared,V)|I], [$(N,shared,V)|II]) :-
    get_implicit_args(Ah,At, I, II).

%:- mode get_implicit_args_(-,?,+).
get_implicit_args_(T,T, []) :- !.
get_implicit_args_([V|Ah],At,[$(_,stream,V)|I]) :- !,
    get_implicit_args_(Ah,At, I).
get_implicit_args_([V1,V2|Ah],At,[$(_,Type,V1-V2,_)|I]) :- oldnew(Type), !,
    get_implicit_args_(Ah,At, I).
get_implicit_args_([V|Ah],At,[$(_,shared,V)|I]) :-
    get_implicit_args_(Ah,At, I).

%:- mode refer_implicit_elem_value(+,+,?,?,+,-).
refer_implicit_elem_value(shared, _, Value, Value, Id,Id) :- !.
refer_implicit_elem_value(stream, Name, Value, Out, Id1,Id2) :- !,
    replace_i_dict(Name, (Out,Value), Id1,Id2).
refer_implicit_elem_value(_, Name, H-T, H-NewH, Id1,Id2) :- % oldnew type
    replace_i_dict(Name, NewH-T, Id1,Id2).

%:- mode make_dict(-).
make_dict(D) :-
  ( recorded(global_implicit_args, (H,T), _) ; H=T ), !,
  ( recorded(local_implicit_args, (T,[]), _) ; T=[] ), !,
    make_dict(H, D).
make_dict([]).

%:- mode make_dict(+,-).
make_dict([],[]) :- !.
make_dict([(Name,Type)|I], [$(Name,Type,V1-V2,no)|II]) :- 
    oldnew(Type), !, make_dict(I, II).
make_dict([(Name,Type)|I], [$(Name,Type,Var)|II]) :-
    make_dict(I, II).

%:- mode arg_name_not_duplicated(+).
arg_name_not_duplicated(Name) :-
    recorded(local_implicit_args, (H,[]), _),
    member(Name, H), !,
    exerror('The name of implicit argument(~w) is duplicated.',[Name]).
arg_name_not_duplicated(_).

not_duplicated(X) :- var(X), !.
not_duplicated([A|L]) :-
    member(A, L), !, fail.
not_duplicated([A|L]) :- not_duplicated(L).

member(_, T) :- var(T), !, fail.
member(A, [A|_]) :- !.
member(A, [_|B]) :- member(A, B).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%:- mode expand_term_(?,?,+,-,+,-,+).
expand_term_(X,X, Ng,Ng, Id,Id, _) :- var(X), !.
expand_term_(X,Y, Ng,Ng, Id,Id, _) :- integer(X), !,
    ( check_overflow(X,Y);
exerror('Integer overflow. ~w',[X]), fail ), !.
expand_term_(X,X, Ng,Ng, Id,Id, _) :- atomic(X), !.
expand_term_(X,Y, Ng1,Ng2, Id1,Id2, Position) :-
    expand_arith(X,Y, Ng1,Ng2, Id1,Id2, Position), !.
expand_term_(X,Y, Ng1,Ng2, Id1,Id2, Position) :- !,
    expand_term(X,Y, Ng1,Ng2, Id1,Id2, Position).

%:- mode expand_term(?,?,+,-,+,-,+).
expand_term(X,X, Ng,Ng, Id,Id, _) :- var(X), !.
expand_term(X,Y, Ng,Ng, Id,Id, _) :- integer(X), !,
    ( check_overflow(X,Y);
	exerror('Integer overflow. ~w',[X]), fail ), !.
expand_term(X,X, Ng,Ng, Id,Id, _) :- atomic(X), !.
expand_term(~(X),Y, Ng1,Ng2, Id1,Id2, Position) :-
    expand_arith(X,Y, Ng1,Ng2, Id1,Id2, Position), !.
expand_term($~(X),Y, Ng1,Ng2, Id1,Id2, Position) :-
    expand_float_arith(X,Y, Ng1,Ng2, Id1,Id2, Position), !.
expand_term(``(X),X, Ng,Ng, Id,Id, _) :- !.
expand_term(`(X),Y, Ng1,Ng2, Id1,Id2, Position) :- !,
    functor(X, Fnc, Nargs),
    expand_arg_elem(0,Nargs, X, Args,[], Ng1,Ng2, Id1,Id2, Position),
    Y =.. [Fnc|Args].						%%880427-KH
expand_term(&X,Y, Ng,Ng, Id1,Id2, _) :- atom(X), !,
    find_implicit_elem(Id1, X, Type, Value),
  ( Type == stream, !, 
        exerror('Implicit arg ~w:~w can not write this position.',[X,Type]),
        Id2=Id1 ;
    Type == shared,!,refer_implicit_elem_value(Type, X, Value, Y, Id1,Id2) ;
    refer_implicit_elem_value(Type, X, Value, Y-Y, Id1,Id2)
    ), !.
expand_term(&X,Y, Ng,Ng, Id,Id, _) :- 
    X=..[ArgName,Which], atom(ArgName),
    ( Which == old ; Which==new ), !,
    find_implicit_elem(Id, ArgName, Type, Value),
    ( Type == oldnew, !, 
         ( Which==old, !, Value=(Y-_) ; Value=(_-Y) ), ! ;
      exerror('This expression (&~w) is illegal type(~w).', [X,Type]) ).
expand_term(&X,Y, Ng1,Ng2, Id1,Id4, body) :- 
    X=..[ArgName,Pos], atom(ArgName), !,
    find_implicit_elem(Id1, ArgName, Type, Value),
    expand_term(Pos, NewPos, true,Ng, Id1,Id2, Position),
    ( ( var(NewPos) ; integer(NewPos) ) ;
      exerror('This expression (&~w) has illegal position (~w).',
	      [X,NewPos]) ), !,
  ( Type == stream, !, 
        exerror('Implicit arg(~w) of this type(~w) can not write this position.',[X,Type]),
        Id3=Id1, Ng1=Ng2 ;
    Type == shared,!,
        refer_implicit_elem_value(Type, ArgName, Value, V, Id2,Id3),
        Ng2=(Ng,set_vector_element(V,NewPos,Y,Y,New),Ng1),
        replace_i_dict(ArgName, New, Id3,Id4) ;
    Type == oldnew,!,
        refer_implicit_elem_value(Type, ArgName, Value, O-N, Id2,Id4),
        Ng2=(Ng,set_vector_element(O,NewPos,Y,Y,N),Ng1) ;
    Type == string,!,
        refer_implicit_elem_value(Type, ArgName, Value, O-N, Id2,Id4),
        Ng2=(Ng,set_string_element(O,NewPos,Y,N),Ng1)
    ), !.
expand_term(&X,Y, Ng1,Ng2, Id1,Id4, Position) :- Position \== body,
    X=..[ArgName,Pos], atom(ArgName), !,
    find_implicit_elem(Id1, ArgName, Type, Value),
    expand_term(Pos, NewPos, true,Ng, Id1,Id2, Position),
  ( Type == stream, !, 
        exerror('Implicit arg(~w) of this type(~w) can not write this position.',[X,Type]),
        Id3=Id1, Ng1=Ng2 ;
    Type == shared,!,
        refer_implicit_elem_value(Type, ArgName, Value, V, Id2,Id4),
        Ng2=(Ng,vector_element(V,NewPos,Y),Ng1) ;
    Type == oldnew,!,
        refer_implicit_elem_value(Type, ArgName, Value, O-O, Id2,Id4),
        Ng2=(Ng,vector_element(O,NewPos,Y),Ng1) ;
    Type == string,!,
        refer_implicit_elem_value(Type, ArgName, Value, O-O, Id2,Id4),
        Ng2=(Ng,string_element(O,NewPos,Y),Ng1)
    ), !.
expand_term(C#B, Y, Ng1,Ng2, Id1,Id2, Position) :- atomic(C), !,
    expand_term(B, B1, Ng1,Ng2, Id1,Id2, Position),
    expand_sharp_macro(C#B1, Y).
expand_term(#B, Y, Ng1,Ng2, Id1,Id2, Position) :- !,
    expand_term(B, B1, Ng1,Ng2, Id1,Id2, Position),
    expand_pre_sharp_macro(#B1, Y).
expand_term({}(A),Y, Ng1,Ng2, Id1,Id2, Position) :-
    flatten_vector_args(A,ArgsL),
    X =.. [{}|ArgsL],
    functor(X, Fnc, Nargs),
    expand_arg_elem(0,Nargs, X, Args,[], Ng1,Ng2, Id1,Id2, Position),
    reconstruct_vector_args(Args,Rargs),
    Y =.. [Fnc,Rargs].
expand_term(X,Y, Ng1,Ng2, Id1,Id2, Position) :- X = '.'(_,_), !,
    functor(X, Fnc, Nargs),
    expand_arg_elem(0,Nargs, X, Args,[], Ng1,Ng2, Id1,Id2, Position),
    ( Args = [Car,Cdr], !, Y = [Car|Cdr];
      Args = [Old,New,Cdr], !, Y = [Old,New|Cdr];
      Y =.. [Fnc|Args] ).
expand_term(X,Y, Ng1,Ng2, Id1,Id2, Position) :-
    functor(X, Fnc, Nargs),
    expand_arg_elem(0,Nargs, X, Args,[], Ng1,Ng2, Id1,Id2, Position),
    Y =.. [Fnc|Args].

%:- mode expand_arg_elem(+,+,+,-,?,+,-,+,-,+).
expand_arg_elem(N,N, X,T,T, Ng,Ng, Id,Id, _) :- !.
expand_arg_elem(K,N, X, Ah,At, Ng1,Ng2, Id1,Id2, Position) :-
    K1 is K+1, arg(K1, X, Xk),
    expand_arg_elem_(K1,N, X, Ah,At, Ng1,Ng2, Id1,Id2, Position, Xk).

%:- mode expand_arg_elem_(+,+,+,-,?,+,-,+,-,+,?).
expand_arg_elem_(K,N, X, [Xk|Ah],At, Ng1,Ng3, Id1,Id3, Position, Xk) :- 
    var(Xk), !,
    expand_arg_elem(K,N, X, Ah,At, Ng1,Ng3, Id1,Id3, Position).
expand_arg_elem_(K,N, X, Ah,At, Ng1,Ng2, Id1,Id3, Position, &Xk) :-
    atom(Xk), !,
    find_implicit_elem(Id1, Xk, Type, Value),
    refer_implicit_elem_value(Type, Xk, Value, Yk, Id1,Id2),
%  ( var(Yk), !, Ah=[Yk|Am] ; Yk=(V1-V2), Ah=[V1,V2|Am] ), !,
   ( ( Type==shared ; Type==stream ), !, Ah=[Yk|Am] ;	% 890808 Nishizaki
       Yk=(V1-V2), Ah=[V1,V2|Am] ), !,
    expand_arg_elem(K,N, X, Am,At, Ng1,Ng2, Id2,Id3, Position).
expand_arg_elem_(K,N, X, Ah,At, Ng1,Ng2, Id1,Id3, body, &Xk) :-
    Xk=..[ArgName,OldNew], atom(ArgName), OldNew==oldnew, !, % 890512 Nishizaki
    find_implicit_elem(Id1, ArgName, Type, Value),
   ( Type==shared ; Type==stream ), !,
    replace_i_dict(ArgName, New, Id1,Id2),
    Ah=[Value,New|Am],
    expand_arg_elem(K,N, X, Am,At, Ng1,Ng2, Id2,Id3, Position).
expand_arg_elem_(K,N, X, [Yk|Ah],At, Ng1,Ng3, Id1,Id3, Position, Xk) :- 
    expand_term(Xk,Yk, Ng1,Ng2, Id1,Id2, Position),
    expand_arg_elem(K,N, X, Ah,At, Ng2,Ng3, Id2,Id3, Position).
/************
expand_arg_elem_(K,N, X, Ah,At, Ng1,Ng4, Id1,Id5, body, &Xk) :-
    Xk=..[ArgName,Pos], atom(ArgName), !,
    find_implicit_elem(Id1, ArgName, Type, Value),
    refer_implicit_elem_value(Type, ArgName, Value, Yk, Id1,Id2),
    expand_term(Pos, NewPos, Ng1,Ng2, Id2,Id3, body),
  ( Type==oldnew, !, Yk=(Old-New), Id4=Id3,
        Ng3=(set_vector_element(Old,NewPos,Elem,Elem,New),Ng2) ;
    Type==string, !, Yk=(Old-New), Id4=Id3,
        Ng3=(string_element(Old,NewPos,Elem,New),Ng2) ;
    Ng3=(set_vector_element(Yk,NewPos,Elem,Elem,New),Ng2),
       replace_i_dict(ArgName, New, Id3,Id4) ), !,
    Ah=[Elem|Am],
    expand_arg_elem(K,N, X, Am,At, Ng3,Ng4, Id4,Id5, body).
expand_arg_elem_(K,N, X, Ah,At, Ng1,Ng4, Id1,Id5, Position, &Xk) :-
    Position \== body, Xk=..[ArgName,Pos], atom(ArgName), !,
    find_implicit_elem(Id1, ArgName, Type, Value),
    refer_implicit_elem_value(Type, ArgName, Value, Yk, Id1,Id2),
    expand_term(Pos, NewPos, Ng1,Ng2, Id2,Id3, Position),
  ( Type==oldnew, !, Yk=(Old-Old),
        Ng3=(vector_element(Old,NewPos,Elem),Ng2), Id4=Id3 ;
    Type==string, !, Yk=(Old-New),
        Ng3=(string_element(Old,NewPos,Elem,New),Ng2), Id4=Id3 ;
    Ng3=(set_vector_element(Yk,NewPos,Elem,Elem,New),Ng2),
       replace_i_dict(ArgName, New, Id3,Id4) ), !,
    Ah=[Elem|Am],
    expand_arg_elem(K,N, X, Am,At, Ng3,Ng4, Id4,Id5, Position).
expand_arg_elem_(K,N, X, Ah,At, Ng1,Ng2, Id1,Id3, Position, &Xk) :-
    atom(Xk), !,
    find_implicit_elem(Id1, Xk, Type, Value),
    refer_implicit_elem_value(Type, Xk, Value, Yk, Id1,Id2),
  ( var(Yk), !, Ah=[Yk|Am] ; Yk=(V1-V2), Ah=[V1,V2|Am] ), !,
    expand_arg_elem(K,N, X, Am,At, Ng1,Ng2, Id2,Id3, Position).
expand_arg_elem_(K,N, X, [Yk|Ah],At, Ng1,Ng3, Id1,Id3, Position, Xk) :-
    Xk \== &_, !,
    expand_term(Xk, Yk, Ng1,Ng2, Id1,Id2, Position),
    expand_arg_elem(K,N, X, Ah,At, Ng2,Ng3, Id2,Id3, Position).
expand_arg_elem_(K,N, X, Ah,At, Ng1,Ng2, Id1,Id2, Position, &Xk) :-
    exerror('Illegal expression. ~n~w', [&Xk]),
    expand_arg_elem(K,N, X, Ah,At, Ng1,Ng2, Id1,Id2, Position).
************/
    
%:- mode expand_arith(?,?, +,-,+,-,+).
expand_arith(X, X, Ng,Ng, Id,Id, _) :- var(X), !.
expand_arith(A+B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
  ( A1 ==  0, !, Y = B1, Ng4 = Ng3;
    B1 ==  0, !, Y = A1, Ng4 = Ng3;
	( A1 ==  1, !, AG = increment(B1, Y);
	  A1 == -1, !, AG = decrement(B1, Y);
	  B1 ==  1, !, AG = increment(A1, Y);
	  B1 == -1, !, AG = decrement(A1, Y);
	  AG = add(A1, B1, Y) ),
	  computable(A1, B1, (X is A1 + B1), X,Y, AG, Ng3,Ng4) ).
expand_arith(A-B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
  ( B1 ==  0, !, Y = A1, Ng4 = Ng3;
        ( A1 ==  0, !, AG = minus(B1, Y);
	  B1 ==  1, !, AG = decrement(A1, Y);
	  B1 == -1, !, AG = increment(A1, Y);
	  AG = subtract(A1, B1, Y) ),
	  computable(A1, B1, (X is A1 - B1), X,Y, AG, Ng3,Ng4) ).
expand_arith(A*B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
  ( A1 ==  0, !, Y = 0, Ng4 = Ng3;
    B1 ==  0, !, Y = 0, Ng4 = Ng3;
	( A1 == -1, !, AG = minus(B1, Y);
	  B1 == -1, !, AG = minus(A1, Y);
	  AG = multiply(A1, B1, Y) ),
	  computable(A1, B1, (X is A1 * B1), X,Y, AG, Ng3,Ng4) ).
expand_arith(A/B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
  ( B1 ==  1, !, Y = A1, Ng4 = Ng3;
      ( B1 == -1, !, AG = minus(A1, Y);
	AG = divide(A1, B1, Y) ),
	computable(A1, B1, (X is A1 // B1), X,Y, AG, Ng3,Ng4) ).
expand_arith((A mod B), Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    computable(A1, B1, (Y is A1 mod B1), modulo(A1, B1, Y), Ng3,Ng4).
expand_arith(A<<B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    computable_unsigned(A1, B1, (X is A1 << B1), X,Y,
	shift_left(A1, B1, Y), Ng3,Ng4).
expand_arith(A>>B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    computable_unsigned(A1, B1, (X is A1 >> B1), X,Y,
	shift_right(A1, B1, Y), Ng3,Ng4).
expand_arith(A/\B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    computable(A1, B1, (Y is A1 /\ B1), and(A1, B1, Y), Ng3,Ng4).
expand_arith(A\/B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    computable(A1, B1, (Y is A1 \/ B1), or(A1, B1, Y), Ng3,Ng4).
expand_arith(A xor B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    computable(A1, B1, (Y is A1 ^ B1), exclusive_or(A1, B1, Y), Ng3,Ng4).
expand_arith(-X, Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
  ( integer(X1), !, Y is -X1, Ng3 = Ng2 ; Ng3 = (Ng2, minus(X1,Y)) ).
expand_arith(\(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, complement(X1, Y)).
expand_arith(abs(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
  ( integer(X1), !,
	( X1 >= 0, !, Y = X1, Ng3 = Ng2;
          X1 < 0, !, Y is -X1, Ng3 = Ng2 );
      Ng3 = (Ng2, abs(X1, Y)) ).
expand_arith(min(A,B), Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
  ( integer(A1), integer(B1), !,
	( A1 =< B1, !, Y = A1, Ng4 = Ng3;
	  A1 >  B1, !, Y = B1, Ng4 = Ng3 );
      Ng4 = (Ng3, min(A1, B1, Y)) ).
expand_arith(max(A,B), Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
  ( integer(A1), integer(B1), !,
	( A1 >= B1, !, Y = A1, Ng4 = Ng3;
    	  A1 <  B1, !, Y = B1, Ng4 = Ng3 );
      Ng4 = (Ng3, max(A1, B1, Y)) ).

expand_arith(int(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_to_integer(X1, Y)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%:- mode expand_float_term_(?,?,+,-,+,-,+).
expand_float_term_(X,X, Ng,Ng, Id,Id, _) :- var(X), !.
expand_float_term_(X,X, Ng,Ng, Id,Id, _) :- atomic(X), !.
expand_float_term_(X,Y, Ng1,Ng2, Id1,Id2, Position) :-
    expand_float_arith(X,Y, Ng1,Ng2, Id1,Id2, Position), !.
expand_float_term_(X,Y, Ng1,Ng2, Id1,Id2, Position) :- !,
    expand_term(X,Y, Ng1,Ng2, Id1,Id2, Position).

%:- mode expand_float_arith(?,?, +,-,+,-,+).
expand_float_arith(X, X, Ng,Ng, Id,Id, _) :- var(X), !.
expand_float_arith(A+B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    Ng4 = (Ng3, floating_point_add(A1, B1, Y)).
expand_float_arith(A-B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    Ng4 = (Ng3, floating_point_subtract(A1, B1, Y)).
expand_float_arith(A*B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    Ng4 = (Ng3, floating_point_multiply(A1, B1, Y)).
expand_float_arith(A/B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    Ng4 = (Ng3, floating_point_divide(A1, B1, Y)).
expand_float_arith(-X, Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_minus(X1, Y)).
expand_float_arith(abs(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_abs(X1, Y)).
expand_float_arith(min(A,B), Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    Ng4 = (Ng3, floating_point_min(A1, B1, Y)).
expand_float_arith(max(A,B), Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    Ng4 = (Ng3, floating_point_max(A1, B1, Y)).
expand_float_arith(floor(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_floor(X1, Y)).
expand_float_arith(sqrt(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_sqrt(X1, Y)).
expand_float_arith(ln(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_ln(X1, Y)).
expand_float_arith(log(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_log(X1, Y)).
expand_float_arith(exp(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_exp(X1, Y)).
expand_float_arith(A**B, Y, Ng1,Ng4, Id1,Id3, Position) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, Position),
    Ng4 = (Ng3, floating_point_pow(A1, B1, Y)).
expand_float_arith(sin(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_sin(X1, Y)).
expand_float_arith(cos(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_cos(X1, Y)).
expand_float_arith(tan(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_tan(X1, Y)).
expand_float_arith(asin(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_asin(X1, Y)).
expand_float_arith(acos(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_acos(X1, Y)).
expand_float_arith(atan(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
  ( var(X), !, Id1 = Id2, Ng3 = floating_point_atan(X, Y);
    X = A/B, !, expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, Position),
	        expand_float_term_(B, B1, Ng2,Ng4, Id2,Id3, Position),
		Ng3 = (Ng4, floating_point_atan(A1, B1, Y));
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_atan(X1, Y)) ).
expand_float_arith(sinh(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_sinh(X1, Y)).
expand_float_arith(cosh(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_cosh(X1, Y)).
expand_float_arith(tanh(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_float_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, floating_point_tanh(X1, Y)).

expand_float_arith(float(X), Y, Ng1,Ng3, Id1,Id2, Position) :- !,
    expand_term_(X, X1, Ng1,Ng2, Id1,Id2, Position),
    Ng3 = (Ng2, integer_to_floating_point(X1, Y)).

%:- mode expand_binary_op(?,?,+,-,+,-,+).
expand_binary_op(A<B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    computable(A1, B1, (A1 < B1), less_than(A1, B1), Y).
expand_binary_op(A=<B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    computable(A1, B1, (A1 =< B1), not_less_than(B1, A1), Y).
expand_binary_op(A>B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    computable(A1, B1, (A1 > B1), less_than(B1, A1), Y).
expand_binary_op(A>=B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    computable(A1, B1, (A1 >= B1), not_less_than(A1, B1), Y).
expand_binary_op(A=:=B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    computable(A1, B1, (A1 =:= B1), equal(A1, B1), Y).
expand_binary_op(A=\=B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    computable(A1, B1, (A1 =\= B1), not_equal(A1, B1), Y).
expand_binary_op(A\=B, diff(A1,B1), Ng1,Ng3, Id1,Id3, guard) :-
    expand_term(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_term(B, B1, Ng2,Ng3, Id2,Id3, guard).
expand_binary_op(A$<B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    Y = floating_point_less_than(A1, B1).
expand_binary_op(A$=<B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    Y = floating_point_not_less_than(B1, A1).
expand_binary_op(A$>B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    Y = floating_point_less_than(B1, A1).
expand_binary_op(A$>=B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    Y = floating_point_not_less_than(A1, B1).
expand_binary_op(A$=:=B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    Y = floating_point_equal(A1, B1).
expand_binary_op(A$=\=B, Y, Ng1,Ng3, Id1,Id3, guard) :- !,
    expand_float_term_(A, A1, Ng1,Ng2, Id1,Id2, guard),
    expand_float_term_(B, B1, Ng2,Ng3, Id2,Id3, guard),
    Y = floating_point_not_equal(A1, B1).

%:- mode expand_assign(?,?).
expand_assign(X, O) :- integer(O), integer(X), X==O, !.
expand_assign(X, O) :- integer(O), var(X), !, X=O.
expand_assign(X, O) :- var(O), integer(X), !, X=O.
expand_assign(X, O) :- var(O), var(X), !, X=O.

%:- mode expand_float_assign(?,?).
expand_float_assign(X, O) :- float(O), float(X), X==O, !.
expand_float_assign(X, O) :- float(O), var(X), !, X=O.
expand_float_assign(X, O) :- var(O), float(X), !, X=O.
expand_float_assign(X, O) :- var(O), var(X), !, X=O.

%:- mode expand_sharp_macro(+,-).
%expand_sharp_macro(c#[X], X) :- integer(X), !.
%expand_sharp_macro(ascii#X, Code) :- atomic(X), ascii_code(X, Code), !.
%expand_sharp_macro(ascii#X, ascii#X) :- ascii_string(X), !.
%expand_sharp_macro(string#X, string#X) :- ascii_string(X), !.
%expand_sharp_macro((module)#X, X) :- atomic(X), !.
%expand_sharp_macro(code#(M:P/A), {M,P,A}) :- !.
%expand_sharp_macro(key#lf, 10) :- !.
%expand_sharp_macro(key#cr, 13) :- !.
%expand_sharp_macro(B#X, Code) :-
%    integer(B), B>=2, B=<36,                       % 880721 Y.Kimura
%    translate_to_digit(X, B, _, Code), !.
%expand_sharp_macro(Pat, Code) :- (Pat=>Code), !.
%expand_sharp_macro(Pat, Pat).

%(Pat=>Pat) :- fail.

expand_sharp_macro(Pat, Exp) :- expand_sharp_macro(Pat, Exp, 0), !.

expand_sharp_macro(c#[X], X, _) :- integer(X), !.
expand_sharp_macro(ascii#X, Code, _) :- atomic(X), ascii_code(X, Code), !.
expand_sharp_macro(ascii#X, ascii#X, _) :- ascii_string(X), !.
expand_sharp_macro(string#X, string#X, _) :- ascii_string(X), !.
expand_sharp_macro((module)#X, X, _) :- atomic(X), !.
expand_sharp_macro(code#(M:P/A), {M,P,A}, _) :- !.
expand_sharp_macro(key#lf, 10, _) :- !.
expand_sharp_macro(key#cr, 13, _) :- !.
expand_sharp_macro(B#X, Code, _) :-
    integer(B), B>=2, B=<36,                       % 880721 Y.Kimura
    translate_to_digit(X, B, _, C),
    check_overflow_unsigned(C, Code), !.
expand_sharp_macro(Pat, Exp, Dep) :-
	(Pat=>Code), expand_sharp_macro(Pat, Exp, Dep, Code), !.
expand_sharp_macro(Pat, Pat, _).

expand_sharp_macro(Pat, Exp, Dep, Code) :- Code = K#D, Dep < 100,
	Dep1 is Dep + 1,
	expand_sharp_macro(Code, Exp, Dep1), !.
expand_sharp_macro(Pat, Exp, Dep, Code) :- Code = K#D,
	warn('# macro definition loop. (~w)',[Pat]), fail.
expand_sharp_macro(Pat, Code, Dep, Code) :- !.

%:- mode expand_pre_sharp_macro(+,-).
expand_pre_sharp_macro(#[X], X) :- integer(X), !.
expand_pre_sharp_macro(#X, #X) :- !.

ascii_string(X):- nonvar(X), ascii_string_(X).	% 890511 Nishizaki

ascii_string_([X|Y]):- integer(X), X>=0, X=<255, ascii_string(Y).
ascii_string_([]).

translate_to_digit([X|Y], B, NN, Code) :-
    digit(X,V), V<B, !,
    translate_to_digit(Y, B, N, C1),
    Code is C1 + (V*N),
    NN is N*B.
translate_to_digit([], _, 1, 0).

flatten_vector_args(A,[A]) :- var(A), !.
flatten_vector_args((A,Args),[A|FL]) :- !,
	flatten_vector_args(Args,FL).
flatten_vector_args(A,[A]) :- !.

reconstruct_vector_args([A],A) :- !.
reconstruct_vector_args([A|Args],(A,RL)) :- !,
	reconstruct_vector_args(Args,RL).


%%%%%%%%%%%%%%%%%
% Common Routine
%

computable(O1, O2, G, X,Y, _, Gs, Gs) :- integer(O1), integer(O2),
  ( call(G), check_overflow(X,Y) ;
    exerror('Evaluation failed. ~w',[G]),	
    !,fail ), !.
computable(_, _, _, _,_, B, Gs, (Gs,B)).

computable_unsigned(O1, O2, G, X,Y, _, Gs, Gs) :- integer(O1), integer(O2),
  ( call(G), check_overflow_unsigned(X,Y) ;
    exerror('Evaluation failed. ~w',[G]),	
    !,fail ), !.
computable_unsigned(_, _, _, _,_, B, Gs, (Gs,B)).

computable(O1, O2, G, _, Gs, Gs) :- integer(O1), integer(O2),
  ( call(G) ;
    exerror('Evaluation failed. ~n~w',[G]),
    !,fail ), !.
computable(_, _, _, B, Gs, (Gs,B)).

computable(O1, O2, G, B, true) :- integer(O1), integer(O2),
  ( call(G) ; 
    exerror('Evaluation failed. ~n~w',[G]),
    !,fail ), !.
computable(_, _, _, B, B).

check_overflow(X,X) :- X =< 2147483647, X >= -2147483648, !.
check_overflow(X,X) :- fail.

check_overflow_unsigned(X,X) :- X =< 2147483647, X >= -2147483648, !.
check_overflow_unsigned(X,Y) :- X =< 4294967295, X >= -4294967296,
	Y is X - 4294967296, !.
check_overflow_unsigned(X,X) :- fail.

digit(48,0) :- !. digit(49,1) :- !. digit(50,2) :- !. digit(51,3) :- !.
digit(52,4) :- !. digit(53,5) :- !. digit(54,6) :- !. digit(55,7) :- !.
digit(56,8) :- !. digit(57,9) :- !. digit(97,10) :- !. digit(65,10) :- !.
digit(98,11) :- !. digit(66,11) :- !. digit(99,12) :- !. digit(67,12) :- !.
digit(100,13) :- !. digit(68,13) :- !. digit(101,14) :- !. digit(69,14) :- !.
digit(102,15) :- !. digit(70,15) :- !. digit(103,16) :- !. digit(71,16) :- !.
digit(104,17) :- !. digit(72,17) :- !. digit(105,18) :- !. digit(73,18) :- !.
digit(106,19) :- !. digit(74,19) :- !. digit(107,20) :- !. digit(75,20) :- !.
digit(108,21) :- !. digit(76,21) :- !. digit(109,22) :- !. digit(77,22) :- !.
digit(110,23) :- !. digit(78,23) :- !. digit(111,24) :- !. digit(79,24) :- !.
digit(112,25) :- !. digit(80,25) :- !. digit(113,26) :- !. digit(81,26) :- !.
digit(114,27) :- !. digit(82,27) :- !. digit(115,28) :- !. digit(83,28) :- !.
digit(116,29) :- !. digit(84,29) :- !. digit(117,30) :- !. digit(85,30) :- !.
digit(118,31) :- !. digit(86,31) :- !. digit(119,32) :- !. digit(87,32) :- !.
digit(120,33) :- !. digit(88,33) :- !. digit(121,34) :- !. digit(89,34) :- !.
digit(122,35) :- !. digit(90,35) :- !.

ascii_code('!',33). ascii_code('"',34). ascii_code('#',35). ascii_code('$',36).
ascii_code('%',37). ascii_code('&',38). ascii_code('''',39). 
ascii_code('(',40).
ascii_code(')',41). ascii_code('*',42). ascii_code('+',43). ascii_code(',',44).
ascii_code('-',45). ascii_code('.',46). ascii_code('/',47). ascii_code('0',48).
ascii_code('1',49). ascii_code('2',50). ascii_code('3',51). ascii_code('4',52).
ascii_code('5',53). ascii_code('6',54). ascii_code('7',55). ascii_code('8',56).
ascii_code('9',57). ascii_code(':',58). ascii_code(';',59). ascii_code('<',60).
ascii_code('=',61). ascii_code('>',62). ascii_code('?',63). ascii_code('@',64).
ascii_code('A',65). ascii_code('B',66). ascii_code('C',67). ascii_code('D',68).
ascii_code('E',69). ascii_code('F',70). ascii_code('G',71). ascii_code('H',72).
ascii_code('I',73). ascii_code('J',74). ascii_code('K',75). ascii_code('L',76).
ascii_code('M',77). ascii_code('N',78). ascii_code('O',79). ascii_code('P',80).
ascii_code('Q',81). ascii_code('R',82). ascii_code('S',83). ascii_code('T',84).
ascii_code('U',85). ascii_code('V',86). ascii_code('W',87). ascii_code('X',88).
ascii_code('Y',89). ascii_code('Z',90). ascii_code('[',91). ascii_code('\',92).
ascii_code(']',93). ascii_code('^',94). ascii_code('_',95). ascii_code('`',96).
ascii_code('a',97). ascii_code('b',98). ascii_code('c',99). 
ascii_code('d',100). ascii_code('e',101). ascii_code('f',102).
ascii_code('g',103). ascii_code('h',104). ascii_code('i',105).
ascii_code('j',106). ascii_code('k',107). ascii_code('l',108).
ascii_code('m',109). ascii_code('n',110). ascii_code('o',111).
ascii_code('p',112). ascii_code('q',113). ascii_code('r',114).
ascii_code('s',115). ascii_code('t',116). ascii_code('u',117).
ascii_code('v',118). ascii_code('w',119). ascii_code('x',120).
ascii_code('y',121). ascii_code('z',122). ascii_code('{',123).
ascii_code('|',124). ascii_code('}',125). ascii_code('~',126).

/************

%:- mode list_variables(?,-,?).
list_variables(X) --> { var(X) }, !, [X].
list_variables(X) --> { atomic(X) }, !.
list_variables(X) --> { functor(X, F, A) }, list_variables(A, X).

%:- mode list_varibles(+,+,-,?).
list_variables(0, _) --> !.
list_variables(K, X) -->
    { arg(K, X, XK) },
    list_variables(XK),
    { K1 is K-1 },
    list_variables(K1, X).
************/

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Utility
%%%%%%%%%%%%%%%%%%%%
%:- mode exerror(+,+).
exerror(Format, Args) :-
    telling(Old), tell(user),
    nl, display('%%% Error in macro expander: '),
    format(Format, Args),
    nl,
    tell(Old).

%:- mode opt_true(+,-).
opt_true(X, Y) :- opt_true(X, true,Y).

%:- mode opt_true(+,+,-).
opt_true((true,true), A,A) :- !.
opt_true((true,Y), A,B) :- !, opt_true(Y, A,B).
opt_true((X,true), A,B) :- !, opt_true(X, A,B).
opt_true((X,Y), A,B) :- !,
    opt_true(Y, A,C), opt_true(X, C,B).
opt_true(G, true,G) :- !.
opt_true(G, T,(G,T)).

%:- mode opt_true_unify(+,-).
opt_true_unify(X, Y) :- opt_true_unify(X, true,Y).

%:- mode opt_true_unify(+,+,-).
opt_true_unify((X=Y,X1=Y1), A,A) :- orvar(X,Y), orvar(X1,Y1), !, X=Y, X1=Y1.
opt_true_unify((X=Y,true), A,A) :- orvar(X,Y), !, X=Y.
opt_true_unify((true,X=Y), A,A) :- orvar(X,Y), !, X=Y.
opt_true_unify((true,true), A,A) :- !.
opt_true_unify((H=T,Y), A,B) :- orvar(H,T), !, H=T, opt_true_unify(Y, A,B).
opt_true_unify((X,H=T), A,B) :- orvar(H,T), !, H=T, opt_true_unify(X, A,B).
opt_true_unify((true,Y), A,B) :- !, opt_true_unify(Y, A,B).
opt_true_unify((X,true), A,B) :- !, opt_true_unify(X, A,B).
opt_true_unify((X,Y), A,B) :- !,
    opt_true_unify(Y, A,C), opt_true_unify(X, C,B).
opt_true_unify(G, true,G) :- !.
opt_true_unify(G, T,(G,T)).

orvar(X,_) :- var(X), !.    orvar(_,X) :- var(X), !.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
translate_dcg_left((H,L),H1,S0,S) :- list_toplevel(L), !,
    dlist(L,S1,S), translate_dcg_atom(H,H1,S0,S1).
translate_dcg_left(H,H1,S0,S) :- translate_dcg_atom(H,H1,S0,S).

%:- mode translate_dcg(?,-,-,-).
translate_dcg(X,(S0=S,X),S0,S) :- var(X), !.
translate_dcg(true,(S0=S),S0,S) :- !.  % 871020 added
translate_dcg((X,[A|Y],Z),(X1,Z1),S0,S) :- list_toplevel(Y), !,
   translate_dcg(X,X1,S0,S1), dlist([A|Y],S1,S2), translate_dcg(Z,Z1,S2,S).
translate_dcg((X,[A|Y]),X1,S0,S) :- list_toplevel(Y), !,
   translate_dcg(X,X1,S0,S1), dlist([A|Y],S1,S).
translate_dcg(({G},Y),(G,Y1),S0,S) :- !, translate_dcg(Y,Y1,S0,S).
translate_dcg((X,{G}),(X1,G),S0,S) :- !, translate_dcg(X,X1,S0,S).
translate_dcg((X,Y),(X1,Y1),S0,S) :- !,
    translate_dcg(X,X1,S0,S1), translate_dcg(Y,Y1,S1,S).
translate_dcg((X->Y),(X->Y1),S0,S) :- !, translate_dcg(Y,Y1,S0,S).
% Insert these four clauses.  88/04/12
% Begin
translate_dcg((X;otherwise),(X1;otherwise),S0,S) :- !,
   translate_dcg(X, X1, S0, S).
translate_dcg((otherwise;X),(otherwise;X1),S0,S) :- !,
   translate_dcg(X, X1, S0, S).
translate_dcg((X;alternatively),(X1;alternatively),S0,S) :- !,
   translate_dcg(X, X1, S0, S).
translate_dcg((alternatively;X),(alternatively;X1),S0,S) :- !,
   translate_dcg(X, X1, S0, S).
% End
translate_dcg((X;Y),(X1;Y1),S0,S) :- !,
   translate_dcg(X,X1,S0,S), translate_dcg(Y,Y1,S0,S).
translate_dcg([],S0=S,S0,S) :- !.
translate_dcg([X|Y],S0=Out,S0,S) :- list_toplevel(Y), !, dlist([X|Y],Out,S).
translate_dcg({G},(S0=S,G),S0,S) :- !.
translate_dcg((Module:Goal@Pragma), (Module:Goal1@Pragma), S0, S) :- !,
   translate_dcg_atom(Goal, Goal1, S0, S).
translate_dcg((Module:Goal),(Module:Goal1),S0,S) :- !,
   translate_dcg_atom(Goal, Goal1, S0, S).
translate_dcg((Goal@Pragma), (Goal1@Pragma), S0, S) :- !,
   translate_dcg_atom(Goal, Goal1, S0, S).
translate_dcg(X,X1,S0,S) :- translate_dcg_atom(X,X1,S0,S).

%:- mode translate_dcg_atom(+, -, ?, ?).
translate_dcg_atom(X,X1,S0,S) :-
    functor(X,F,A), A1 is A+1, A2 is A+2, functor(X1,F,A2),
    copy_args(A,X,X1), arg(A1,X1,S0), arg(A2,X1,S).

%:- mode copy_args(+, +, + ).
copy_args( 0, _, _ ) :- !.
copy_args( A, H0, H1 ) :-
    arg( A, H0, Arg ), arg( A, H1, Arg ),
    A1 is A-1, copy_args( A1, H0, H1 ).


clear_implicit_args :- recorded(global_implicit_args, _, Id), erase(Id), fail.
clear_implicit_args :- recorded(local_implicit_args, _, Id), erase(Id), fail.
clear_implicit_args.


%%% EXPANSION OF CASES

case_expansion(X,      X,       _, _, _) --> {var(X)}, !.
case_expansion(true,   true,    _, _, _) --> !. 
case_expansion((X,Y),  (X1,Y1), O, P, Type) --> !, 
    case_expansion(X, X1, O+Y, P, Type), case_expansion(Y, Y1, O+X, P, Type).
case_expansion((X->Y), Z,       O, P, Type) --> !, 
    case_expand((X->Y), Z, O, P, Type).
case_expansion((X;Y),  Z,       O, P, Type) --> !, 
    case_expand((X;Y), Z, O, P, Type).
case_expansion(X,      X,       _, _, _) --> [].

case_expand(Cases, Call, Outside, Pred, Type) -->
    { list_variables(Cases,Vars1,[]),
      list_variables(Outside,Vars2,[]),
      sort(Vars1, Vars1S),
      sort(Vars2, Vars2S),
      intersection(Vars1S,Vars2S,Vars),
      new_functor(Pred, F), Call=..[F|Vars]},
    case_expand_clauses(Cases, Pred, Call, Type).

:- mode list_variables(?,-,?).
list_variables(X) --> { var(X) }, !, [X].
list_variables(X) --> { atomic(X) }, !.
list_variables(X) --> { functor(X, F, A) }, list_variables(A, X).

:- mode list_varibles(+,+,-,?).
list_variables(0, _) --> !.
list_variables(K, X) -->
    { arg(K, X, XK) },
    list_variables(XK),
    { K1 is K-1 },
    list_variables(K1, X).

:- mode intersection(+, +, -).
intersection([], _, []) :- !.
intersection(_, [], []) :- !.
intersection([X|Xs], [Y|Ys], Zs) :- X@<Y, !, intersection(Xs, [Y|Ys], Zs).
intersection([X|Xs], [Y|Ys], Zs) :- X@>Y, !, intersection([X|Xs], Ys, Zs).
intersection([X|Xs], [Y|Ys], [X|Zs]) :- intersection(Xs, Ys, Zs).

:- mode new_functor(+, -).
new_functor(F/A, Functor) :-
   name(F, Fn), dlist(Fn, X1, [47 | X2]),
   name(A, An), dlist(An, X2, [95 | X3]),
   recorded('$$$new_unique_number_for_case_expansion', N, REF), !,
   erase(REF),
   N1 is N+1,
   recorda('$$$new_unique_number_for_case_expansion', N1, _),
   name(N, X3), X0=[36 | X1], name(Functor, X0).

:- mode case_expand_clauses(?, +, -, -, ?, +).
case_expand_clauses(X,        _,    _, _ ) --> {var(X)}, !,
   { error('Uninstantiated case') }.
case_expand_clauses(otherwise, Pred, Call, _) --> !, [otherwise].
case_expand_clauses(alternatively, Pred, Call, _) --> !, [alternatively].
case_expand_clauses((X;Y), Pred, Call, Type) -->
    case_expand_clauses(X, Pred, Call, Type),
    case_expand_clauses(Y, Pred, Call, Type).
case_expand_clauses((X->Y), Pred, Call, no_imp) --> !,   
    {copy_term((Call :- X | Y), (Head :- Guard | B))},
    [(Head :- Guard | Body)],
    case_expansion(B, Body, Head+Guard, Pred, no_imp).
case_expand_clauses((X->Y), Pred, Call, imp) --> !,   
    {copy_term((Call --> X | Y), (Head --> Guard | B))},
    [(Head --> Guard | Body)],
    case_expansion(B, Body, Head+Guard, Pred, imp).
case_expand_clauses(X,        _,    _, _   ) -->
    { ( numbervars(X, 0, _), error('Illegal case: ~w', [X]), fail;
      true ) }.

dlist([]) --> [].
dlist([X|Y]) --> [X], dlist(Y).

list_toplevel(X) :- nonvar(X), (X=[] ; X=[_|Y], list_toplevel(Y)).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
/*****
read_user_macro_definition(Mac):- atom(Mac), !,
	compile(Mac).
read_user_macro_definition(Macs):-
	name(Mac,Macs),
	compile(Mac).
*****/
/*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
read_user_macro_definition(Files) :-
    '$$$user_macro_definition_list'(Defs),
    get_user_macro_definition_list(Files, Files1, []),
    sort(Files1, Files2), sort_1(Files2, Files3),
    replace_user_definition(Defs, Files3).

get_user_macro_definition_list((Car, Cdr), Files0, Files2) :- !,
    get_user_macro_definition_list(Car, Files0, Files1),
    get_user_macro_definition_list(Cdr, Files1, Files2).
get_user_macro_definition_list(File, [File|Files], Files) :- 
    atom(File).

replace_user_definition(Defs, Defs) :- !.
replace_user_definition(Defs, NewDefs) :-
%    warn('User defined macros are to be replaced.',[]),
    abolish((=>)/2),
    assert_new_macro(NewDefs),
    retract(('$$$user_macro_definition_list'(_))),
    assert(('$$$user_macro_definition_list'(NewDefs))).

assert_new_macro([]) :- !.
assert_new_macro([One|Defs]) :- !,
    gen_full_file_name(One, File_name),
    seeing(Old),
    consult_one_file(File_name),
    see(Old),
    assert_new_macro(Defs).

gen_full_file_name(One, File_name) :-
    name(One, OneList),
    macro_library_directory(Library_directory),
    library_name_append(Library_directory, OneList, File_nameList),
    name(File_name, File_nameList).

library_name_append([A|X], Y, [A|Z]) :- !,
    library_name_append(X, Y, Z).
library_name_append([], Y, Y).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Prolog version only

user_macro(X).
*/
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
:- prolog_flag(redefine_warnings, _, off).

:- public read_user_macro_definition/1.
read_user_macro_definition(Macros):- !,
	read_user_macro_definition(Macros,[],DefList),
	assert_definition_list(DefList).

read_user_macro_definition((M,Macros),DL0,DL2):- !,
	read_one_user_macro_definition(M,DL0,DL1),
	read_user_macro_definition(Macros,DL1,DL2).
read_user_macro_definition(M,DL0,DL1):- !,
	read_one_user_macro_definition(M,DL0,DL1).

read_one_user_macro_definition(Mac,DL0,DL1):- atom(Mac), !,
	display('Use macro library : '), display(Mac), ttynl,
	name(Mac,Macs), macro_library_directory(Dir),
	append(Dir,Macs,EMacs), name(EMac,EMacs),
	read_def_one_file(EMac,DL0,DL1).
read_one_user_macro_definition(Macs,DL0,DL1):- !,
	name(Mac,Macs),
	display('Use macro library : "'), display(Mac), display('"'), ttynl,
	read_def_one_file(Mac,DL0,DL1).

append([H|A],B,[H|C]):- append(A,B,C).
append([],X,X).

read_def_one_file(File,DL0,DL1) :- !,
	seeing(Old),
	see(File),
	read(Def),
	read_one_def(Def,DL0,DL1),
	seen,
	see(Old).

read_one_def(end_of_file,DL,DL) :- !.
read_one_def((:- user_macro Name),DL0,DL1) :- !,
	read(Def2), read_one_def(Def2,DL0,DL1).
read_one_def(Def,DL0,DL1) :- read(Def2), read_one_def(Def2,[Def|DL0],DL1).

assert_definition_list([]) :- !.
assert_definition_list([Def|DL]) :- !, assert(Def), assert_definition_list(DL).
