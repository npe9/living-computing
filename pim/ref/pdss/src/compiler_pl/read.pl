%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% READ ROUTINE FOR KL1 COMPILER

:- mode read_clause(+, -, +, +).
read_clause(Clause0, Clause1, Flags, EX) :- 
    my_expand_term(Clause0, Clause1, Cases0, EX),
    ( Cases0 = [One|Rest], !, 
	reconstruct_clauses(Cases0, Cases1, CnL),
        One = ( H :- B | G ), functor( H, F, A ),
        ( compile_by_option(F/A, Cases1, CnL, Flags, []), fail;
%	  display(F/A), display(','), ttyflush );
	  display(F),display('/'),display(A), display(','), ttyflush );
      true ).

:- mode cl_read(-, +, +).
cl_read(Y, Flags, EX) :-
   read(X),
   read_clause(X, Y, Flags, EX).

:- mode reconstruct_clauses(+, -, -).
reconstruct_clauses([], [], []) :- !.
reconstruct_clauses(Clauses0, Clauses1, Clause_No_List) :-
    read_till_break(Clauses0, Break, One_block, Rest0, 0-Count),
  ( Rest0=[], !, 
	Clauses1 = [One_block], 
	Clause_No_List = [Count] ;
    Clauses1 = [One_block, Break|Rest1],
	Clause_No_List = [Count, 0|Cdr_of_list],
	reconstruct_clauses(Rest0, Rest1, Cdr_of_list) ).

:- mode read_till_break(+, -, -, -, +).
read_till_break([One|Rest0], One, [], Rest0, C0-C0) :-
   ( One=otherwise, !; One=alternatively ), !.
read_till_break([One|Rest0], Break, [One|Rest_block], Rest1, C0-C2) :- !,
    C1 is C0+1,
    read_till_break(Rest0, Break, Rest_block, Rest1, C1-C2).
read_till_break([], [], [], [], C0-C0).


%%%%% DCG EXPANSION

:- mode my_expand_term( +, -, -, +).       % 880712 Y.Kimura To introduce
my_expand_term(X,L, Cases, EX) :-           %  New macro routine
   translate_clause( X, L, Cases, EX).

/**********                              880712 Y.Kimura
:- mode my_expand_term( +, -, -).
my_expand_term(X,L, Cases) :-
   translate_clause( X, Y),
   ( var(Y), !, L = Y, Cases = [];

     Y = ( :- _ ), !, L = Y, Cases = [];
     Y = (H :- Z), var(Z), !, L = Y, Cases = [], functor( H, F, A );
     Y = (H :- Z), Z = (C1|C2), C1 = (_->_),!, 
        warn( 'This predicate has no commit operator !~n~w', [X]),
        my_expand_term((H:-true|(C1;C2)), L, Cases );
     Y = (H :- Z), Z = (G | B),!, L = (H :- G | B1),
        functor( H, F, A ),
	case_expansion(B, B1, H+G, F/A, Cases, []);
     Y = (H :- B), !, L = (H :- true | B1), 
	functor(H, F, A), case_expansion(B, B1, H, F/A, Cases, []);
     L = Y, Cases = [] ).
**********/

/* Replaced by the latest version of Macro expansion routine 
   880621. Y.Kimura
:- mode my_expand_term( +, -, -).
my_expand_term(X,L, Cases) :-
    my_expand_term_1(X, L0, Cases0),
    expand_one_clause(L0, L, Cases0, Cases).

:- mode my_expand_term_1( +, -, -).
my_expand_term_1(X, L, Cases) :-
   my_term_expansion(X, Y),
   ( Y = ( :- _ ), !, L = Y, Cases = [];
     Y = (H :- (C1|C2)), C1 = (_->_),!, 
        warn( 'This predicate has no commit operator !~n~w', [X]),
        my_expand_term((H:-true|(C1;C2)), L, Cases);
     Y = (H :- (G|B)), !, L = (H :- G | B1),
        functor( H, F, A ), case_expansion(B, B1, H+G, F/A, Cases, []);
     Y = (H :- B), !, L = (H :- true | B1), 
	functor(H, F, A), case_expansion(B, B1, H, F/A, Cases, []);
     L = Y, Cases = [] ).
*/

:- mode my_term_expansion(+, -).
my_term_expansion(( :- A ), ( :- A ) ) :- !.
my_term_expansion((H :- G|(C1;C2)), ( H :- G|(C1;C2) ) ) :-
	\+( G = (_->_) ), !.
my_term_expansion((H :- G|B ), ( H :- true|(G;B) ) ) :- G = (_->_), !,
        warn('This predicate has no commit operator !~n~w', [(H:-G|B)]).
my_term_expansion((H :- G|B ), ( H :- G|B) ) :- !.
my_term_expansion((H :- B), ( H :- true | B ) ) :- !,
	warn('This predicate has no commit operator !~n~w', [(H:-B)]).
my_term_expansion((H-->G|B ), ( H1 :- true|(G1;B1) ) ) :- G = (_->_), !,
	warn('This predicate has no commit operator !~n~w', [(H-->G|B)]),
        translate_dcg_left(H,H1,S0,S), translate_dcg((G;B),(G1;B1),S0,S).
my_term_expansion((H-->G|B), (H1:-G|B1)) :- !,
        translate_dcg_left(H,H1,S0,S), translate_dcg(B,B1,S0,S).
my_term_expansion((H-->B), (H1:-true|B1) ) :- !,
	warn('This predicate has no commit operator !~n~w', [(H-->B)]),
        translate_dcg_left(H,H1,S0,S), translate_dcg(B,B1,S0,S).
my_term_expansion( otherwise, otherwise ) :- !.
my_term_expansion( alternatively, alternatively ) :- !.
my_term_expansion( end_of_file, end_of_file ) :- !.
my_term_expansion( H, (H:-true|true)) :-
	warn('This predicate has no commit operator !~n~w', [H]).

/*****
88.06.21 Commented out by Y.Kimura to use new macro expansion routine
translate_dcg_left((H,L),H1,S0,S) :- list_toplevel(L), !,
    dlist(L,S1,S), translate_dcg_atom(H,H1,S0,S1).
translate_dcg_left(H,H1,S0,S) :- translate_dcg_atom(H,H1,S0,S).
*****/

/*****
88.06.21 Commented out by Y.Kimura to use new macro expansion routine
:- mode translate_dcg(?,-,-,-).
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
translate_dcg((X;Y),(X1;Y1),S0,S) :- !,
   translate_dcg(X,X1,S0,S), translate_dcg(Y,Y1,S0,S).
translate_dcg([],S0=S,S0,S) :- !.
translate_dcg([X|Y],S0=Out,S0,S) :- list_toplevel(Y), !, dlist([X|Y],Out,S).
translate_dcg({G},(S0=S,G),S0,S) :- !.
translate_dcg((Module:Goal),(Module:Goal1),S0,S) :- !,
   translate_dcg_atom(Goal, Goal1, S0, S).
translate_dcg((Goal@Pragma), (Goal1@Pragma), S0, S) :- !,
   translate_dcg_atom(Goal, Goal1, S0, S).
translate_dcg(X,X1,S0,S) :- translate_dcg_atom(X,X1,S0,S).
*****/

/*****
88.06.21 Commented out by Y.Kimura to use new macro expansion routine
:- mode translate_dcg_atom(+, -, ?, ?).
translate_dcg_atom(X,X1,S0,S) :-
    functor(X,F,A), A1 is A+1, A2 is A+2, functor(X1,F,A2),
    copy_args(A,X,X1), arg(A1,X1,S0), arg(A2,X1,S).
*****/

/*****
88.06.21 Commented out by Y.Kimura to use new macro expansion routine
:- mode copy_args(+, +, + ).
copy_args( 0, _, _ ) :- !.
copy_args( A, H0, H1 ) :-
    arg( A, H0, Arg ), arg( A, H1, Arg ),
    A1 is A-1, copy_args( A1, H0, H1 ).
*****/
/***** 88.07.12. Commented out Y.Kimura
:- mode dlist(+, -, ?).
dlist([]) --> [].
dlist([X|Y]) --> [X], dlist(Y).
*****/
/***** 88.07.12. Commented out Y.Kimura
list_toplevel(X) :- nonvar(X), (X=[] ; X=[_|Y], list_toplevel(Y)).
*****/

%%% EXPANSION OF CASES

case_expansion(X,      X,       _, _) --> {var(X)}, !.
case_expansion(true,   true,    _, _) --> !. 
case_expansion((X,Y),  (X1,Y1), O, P) --> !, 
    case_expansion(X, X1, O+Y, P), case_expansion(Y, Y1, O+X, P).
case_expansion((X->Y), Z,       O, P) --> !, 
    case_expand((X->Y), Z, O, P).
case_expansion((X;Y),  Z,       O, P) --> !, 
    case_expand((X;Y), Z, O, P).
case_expansion(X,      X,       _, _) --> [].

case_expand(Cases, Call, Outside, Pred) -->
    { list_variables(Cases,Vars1,[]),
      list_variables(Outside,Vars2,[]),
      sort(Vars1, Vars1S),
      sort(Vars2, Vars2S),
      intersection(Vars1S,Vars2S,Vars),
      new_functor(Pred, F), Call=..[F|Vars]},
    case_expand_clauses(Cases, Pred, Call).

/*
   The following two predicates list_variables/3 and list_variables/4 are
   redefined in the file Macro.pl. So, these are commented out.
   88.05.17. Y.Kimura
*/
/*
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
*/
/*****  Commented out Y.Kimura 88.07.12
:- mode intersection(+, +, -).
intersection([], _, []) :- !.
intersection(_, [], []) :- !.
intersection([X|Xs], [Y|Ys], Zs) :- X@<Y, !, intersection(Xs, [Y|Ys], Zs).
intersection([X|Xs], [Y|Ys], Zs) :- X@>Y, !, intersection([X|Xs], Ys, Zs).
intersection([X|Xs], [Y|Ys], [X|Zs]) :- intersection(Xs, Ys, Zs).
*****/
/*****  Commented out Y.Kimura 88.07.12
:- mode new_functor(+, -).
new_functor(F/A, Functor) :-
   name(F, Fn), dlist(Fn, X1, [47 | X2]),
   name(A, An), dlist(An, X2, [95 | X3]),
   recorded('$$$new_unique_number_for_case_expansion', N, REF), !,
   erase(REF),
   N1 is N+1,
   recorda('$$$new_unique_number_for_case_expansion', N1, _),
   name(N, X3), X0=[36 | X1], name(Functor, X0).
*****/
/*****  Commented out Y.Kimura 88.07.12
:- mode case_expand_clauses(?, +, -, -, ?).
case_expand_clauses(X,        _,    _   ) --> {var(X)}, !,
   { error('Uninstantiated case') }.
case_expand_clauses(otherwise, Pred, Call) --> !, [otherwise].
case_expand_clauses(alternatively, Pred, Call) --> !, [alternatively].
case_expand_clauses((X;Y), Pred, Call) -->
    case_expand_clauses(X, Pred, Call),
    case_expand_clauses(Y, Pred, Call).
case_expand_clauses((X->Y), Pred, Call) --> !,   
    {copy_term((Call :- X | Y), (Head :- Guard | B))},
    [(Head :- Guard | Body)],
    case_expansion(B, Body, Head+Guard, Pred).
case_expand_clauses(X,        _,    _   ) -->
    { ( numbervars(X, 0, _), error('Illegal case: ~w', [X]), fail;
      true ) }.
*****/
