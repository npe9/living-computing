%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% HELPER PREDICATE

/*** generating an abstract code ***/
:- mode gen(+, +, -, -, -).
gen(Instr, PC0, PC) --> { PC is PC0+1 }, [Instr].

/*** numbering variables ***/

:- mode number_variables(?, +, -).
number_variables(X, N0, N) :- var(X), !, 
    create_kl1_var(X, N0, N).
number_variables(X, N, N) :- atomic(X), !.
number_variables(X, N, N) :- kl1_var(X), !.
number_variables(X, N0, N) :-
    functor(X, _, A), number_args(A, X, N0, N).

:- mode number_args(+, +, +, -).
number_args(0, _, N, N) :- !.
number_args(K, X, N0, N) :-
    arg(K, X, XK), number_variables(XK, N0, N1),
    K1 is K-1, number_args(K1, X, N1, N).

/***** get the number of variables in a KL1 clause *****/

:- mode get_the_number_of_variables(+, -).
get_the_number_of_variables(c(Aux, _, _, _), Nv) :- arg(1, Aux, Nv).

:- mode create_kl1_var(-, +, -).
create_kl1_var('$VAR'(N0), N0, N1) :- N1 is N0+1.

/*** basic oprations of variables ***/

:- mode var_no(+, ?).
var_no('$VAR'(N), N).

:- mode var_aux(+, +, ?, +).
var_aux(type, V, T, Type-Attr) :- !, var_type(Type, V, T).
var_aux(attr, V, A, Type-Attr) :- !, var_attr(Attr, V, A).

:- mode set_var_aux(+, +, ?, +, ?).
set_var_aux(type, V, T, Type0-Attr, Type1-Attr) :- !,
    set_var_type(Type0, V, T, Type1).
set_var_aux(attr, V, A, Type-Attr0, Type-Attr1) :- !,
    set_var_attr(Attr0, V, A, Attr1).

:- mode var_type(+, +, ?).
var_type(Type, '$VAR'(N), V) :- aref(Type, N, V).

:- mode set_var_type(+, +, ?, -).
set_var_type(Type0, '$VAR'(N), V, Type) :- aset(Type0, N, V, Type).

:- mode var_no_type(+, +, ?).
var_no_type(Type, N, V) :- aref(Type, N, V).

:- mode set_var_no_type(+, +, ?, -).
set_var_no_type(Type0, N, V, Type) :- aset(Type0, N, V, Type).

:- mode var_attr(+, +, ?).
var_attr(Attr, '$VAR'(N), V) :- aref(Attr, N, V).

:- mode set_var_attr(+, +, ?, -).
set_var_attr(Attr0, '$VAR'(N), V, Attr) :-
    aref(Attr0, N, V0), 
    merge_aux_list([V], V0, New), aset(Attr0, N, New, Attr).

:- mode var_no_attr(+, +, ?).
var_no_attr(Attr, N, V) :- aref(Attr, N, V).

:- mode set_var_no_attr(+, +, ?, -).
set_var_no_attr(Attr0, N, V, Attr) :-
    aref(Attr0, N, V0),
    merge_aux_list([V], V0, New), aset(Attr0, N, New, Attr).

:- mode associate_vars(+, +, +, ?).
associate_vars('$VAR'(F), '$VAR'(T), Type0-Attr0, Type-Attr) :- 
    var_no_type(Type0, F, Ftype),
    set_var_no_type(Type0, T, Ftype, Type),
    var_no_attr(Attr0, F, Fattr), var_no_attr(Attr0, T, Tattr),
    merge_aux_list(Fattr, Tattr, NewAttr),
    set_var_no_type(Attr0, F, NewAttr, Attr1),
    set_var_no_type(Attr1, T, NewAttr, Attr).

:- mode merge_aux_list(+, +, -).
merge_aux_list([], To, To) :- !.
merge_aux_list([A|Cdr], To, [A|Z]) :- !, 
    merge_aux_list(Cdr, To, Z).

:- mode check_var_instantiated(+, +).
check_var_instantiated('$VAR'(N), Type-Attr) :-
    var_no_type(Type, N, VType), VType \== [].

:- mode check_var_unbound(+, +).
check_var_unbound('$VAR'(N), Type-Attr) :-
    var_no_type(Type, N, []).    

:- mode set_attribute_and_life_time(+, +, +, +, -, +, ?).
set_attribute_and_life_time(X, A, PC, Tabs0, Tabs, 
                                      Type-Attr0, Type-Attr) :-
    check_legal_attribute(A, V),
    refvar(V, PC, Tabs0, Tabs),
    set_var_attr(Attr0, X, A, Attr).

:- mode check_legal_attribute(+, -).
check_legal_attribute(car(V), V) :- !.          % Attr is one of the form:
check_legal_attribute(cdr(V), V) :- !.          % element(X,index), car(X),
check_legal_attribute(vector(V,_), V) :- !.     % cdr(X), vector(X,Index) or
check_legal_attribute(element(V,_), V) :- !.    % cdr(X), where X is variable
check_legal_attribute(V, []) :- !,
    error('Illegal attribute found: ~w', [V]).

:- mode set_life_time(+, +, +, +, -).
set_life_time(0, _,  _, Tabs, Tabs) :- !.
set_life_time(N, T, PC, Tabs0, Tabs) :-    
    arg(N, T, A), 
    set_life_time_one_var(A, PC, Tabs0, Tabs1),
    N1 is N - 1, set_life_time(N1, T, PC, Tabs1, Tabs).

:- mode set_life_time_one_var(+, +, +, -).
set_life_time_one_var(A, PC, Tabs0, Tabs1) :-
    ( newvar(A, PC, Tabs0, Tabs1), ! ;
      refvar(A, PC, Tabs0, Tabs1) ).

:- mode check_life_time(+, +, +).
check_life_time(PC, X, From-To) :- 
    aref(From, X, F), aref(To, X, T), 
    F =< PC, PC < T, !.

:- mode newvar(+, +, +, -).
newvar(Var, PC, From0-To0-Ref0, From-To-Ref) :- 
    arg(1, Var, X), aref(From0, X, []),
    aset(From0, X, PC, From), aset(To0, X, PC, To),
    aset(Ref0, X, 1, Ref).

:- mode refvar(+, +, +, -).
refvar(Var, PC, From-To0-Ref0, From-To-Ref) :-
    arg(1, Var, X), aset(To0, X, PC, To),
    aref(Ref0, X, C0), C is C0+1, aset(Ref0, X, C, Ref).

:- mode transfer_ref_count(+, +, +, -).
transfer_ref_count('$VAR'(Fn), '$VAR'(Tn), From-To-Ref0, From-To-Ref) :-
    aref(Ref0, Fn, C), aset(Ref0, Tn, C, Ref).

:- mode usereg(+, +, +, -).
usereg(Var, N, Reg0, Reg) :-
    arg(1, Var, X), aset(Reg0, X, N, Reg).

:- mode ref_To_table(+, +, -).
ref_To_table(Var, To, Res) :- 
    arg(1, Var, X), aref(To, X, Res).

:- mode set_To_table(+, +, +, -).
set_To_table(Var, N, To0, To) :- 
    arg(1, Var, X), aset(To0, X, N, To).

:- mode mrb_body_ref(+, +, -).
mrb_body_ref(X, Body0, Body) :- kl1_var(X),
    var_no(X, N),
    aref(Body0, N, Old), New is Old + 1, aset(Body0, N, New, Body).

:- mode set_mrb_body_ref(+, +, +, -).
set_mrb_body_ref(0, _, Body, Body) :- !.
set_mrb_body_ref(N, X, Body0, Body)  :-  arg(N, X, A), atomic(A), !,
    N1 is N - 1, set_mrb_body_ref(N1, X, Body0, Body).
set_mrb_body_ref(N, X, Body0, Body)  :-  arg(N, X, A), 
    mrb_body_ref(A, Body0, Body1),
    N1 is N - 1, set_mrb_body_ref(N1, X, Body1, Body).

/***************************/
/*** KL1 data type check ***/
/***************************/

:- mode kl1_var(?).
kl1_var(X) :- nonvar(X), functor(X, '$VAR', 1).

:- mode kl1_nonvar(?).
kl1_nonvar(X) :- nonvar(X), functor(X, '$VAR', 1), !, fail.
kl1_nonvar(X).

:- mode kl1_string(?).
kl1_string(X) :- nonvar(X), functor(X, '$SCNST', 2), !,
    arg(1, X, Type), ( Type == string, ! ; Type == ascii ).

:- mode kl1_type_of(+, ?).
kl1_type_of([],     nil         ) :- !.
kl1_type_of({},     vector(0)   ) :- !.
kl1_type_of(X,      atom        ) :- atom(X), !.
kl1_type_of(X,      integer     ) :- integer(X), !.
kl1_type_of(X,      float       ) :- float(X), !.	% 890404 Nishizaki
kl1_type_of(X,      var         ) :- kl1_var(X), !.
kl1_type_of(X,      list        ) :- functor(X, '$LIST', 2), !.
kl1_type_of(X,      vector(A)   ) :- functor(X, '$VECT', A), !.
kl1_type_of(X,      string(Type)) :- functor(X, '$SCNST', 2), !,
    arg(1, X, Type), ( Type == string, ! ; Type == ascii ).

/*** hashing function ***/
/* This function takes any KL1 term and returns integer between 0 and 127 */

:- mode kl1_hash(?, -).
kl1_hash(X, 0) :- var(X), !.
kl1_hash(X, Y) :- integer(X), !, 
    Z is (X << 16) \/ X, Y is (Z >> 12) /\ 127.
kl1_hash(X, Y) :- atom(X), !, name(X, U),
    kl1_atom_to_number(U, 0, Z), Y is (Z >> 12) /\ 127.
kl1_hash(X, Y) :- functor(X, F, _), !, arg(1, X, A),
    kl1_hash(F, U), kl1_hash(A, V), Z is (U << 3),
    Y is (Z + V) /\ 127.

:- mode kl1_atom_to_number(+, +, -).
kl1_atom_to_number([], X, X) :- !.
kl1_atom_to_number([X], Y, Z) :- !, U is (X << 4), Z is (Y \/ U) /\ 127.
kl1_atom_to_number([A,B|C], X0, X) :- !, 
    U is (A << 4), V is U \/ B, X1 is (X0 \/ V) /\ 127,
    kl1_atom_to_number(C, X1, X). 

/*** Explicit unification routine ***/

:- mode explicit_unification(?, ?).
explicit_unification(X, X) :- !.
explicit_unification(X, Y) :- 
    error('Guard unification always fails: ~w', [X=Y]).

%%%%% ARRAY MANIPULATION PREDICATES
/*
:- mode array(+, -).
array(Size, Array) :- functor(Array, '$array', Size).

:- mode array(+, -, ?).
array(Size, Array, Init) :-
    array(Size, Array),
    init_array(Size, Array, Init).

:- mode init_array(+, +, ?).
init_array(0, Array, Init) :- !.
init_array(Size0, Array, Init) :-
    Size1 is Size0 - 1,
    aset(Array, Size1, Init, Array),
    init_array(Size1, Array, Init).

:- mode aset(+,+,+,-).
aset(Array,Key,Data,Array) :- Key1 is Key+1, setarg(Key1, Array, Data).

:- mode aref(+,+,?).
aref(Array, Key, Data) :- Key1 is Key+1, arg(Key1, Array, Data).
*/

:- mode array(+, -).
array(Size, Array) :- Size =< 128, !, functor(Array, '$array', Size).
array(Size, Array) :- Rem is (Size >> 7)+1, Size0 is (Size /\ 127),
     functor(Array, '$$array', Rem),
     create_array_loop(Rem, 1, Size0, Array).

:- mode create_array_loop(+, +, +, +).
create_array_loop(1, Key, Size, Array) :- !,
     functor(Sub, '$array', Size), setarg(Key, Array, Sub).
create_array_loop(Rem, Key, Size, Array) :- 
     functor(Sub, '$array', 128), setarg(Key, Array, Sub),
     Rem1 is Rem-1, Key1 is Key+1,
     create_array_loop(Rem1, Key1, Size, Array).

:- mode array(+, -, ?).
array(Size, Array, Init) :-
    array(Size, Array),
    init_array(Size, Array, Init).

:- mode init_array(+, +, ?).
init_array(0, Array, Init) :- !.
init_array(Size0, Array, Init) :-
    Size1 is Size0 - 1,
    aset(Array, Size1, Init, Array),
    init_array(Size1, Array, Init).

:- mode aset(+,+,+,-).
aset(Array,Key,Data,Array) :- functor(Array, '$array', _), !,
    Key1 is Key+1, setarg(Key1, Array, Data).
aset(Array,Key,Data,Array) :- functor(Array, '$$array', _), !,
    Rem is (Key >> 7)+1, Key1 is (Key /\ 127)+1,
    arg(Rem, Array, Sub), setarg(Key1, Sub, Data).

:- mode aref(+,+,?).
aref(Array, Key, Data) :- functor(Array, '$array', _), !,
    Key1 is Key+1, arg(Key1, Array, Data).
aref(Array, Key, Data) :- functor(Array, '$$array', _), !,
    Rem is (Key >> 7)+1, Key1 is (Key /\ 127)+1,
    arg(Rem, Array, Sub), arg(Key1, Sub, Data).


%%%%% Indexing option

:- mode intern_index_pred(+, +, +, ?).
intern_index_pred((One, Preds), Flag, Old, New) :- !,
    update_tree(Old, One, Flag, Old1),
    intern_index_pred(Preds, Flag, Old1, New).
intern_index_pred(Pred, Flag, Old, New) :- 
    update_tree(Old, Pred, Flag, New).

:- mode to_be_compiled_with_index(+, +, +, +).
to_be_compiled_with_index(0, _, _, _) :- !, fail.
to_be_compiled_with_index(_, Pred, _, It) :-
    get_tree(It, Pred, Flag), Flag \== [], !,
  ( Flag == 1, ! ; fail ).
to_be_compiled_with_index(_, _, Cn, _) :-
    number_of_clauses_to_be_compiled_with_index(CNO), 
    Cn > CNO, !.


%%%% Tree manipulation

:- mode get_tree(+,+,?).
get_tree([], _, []) :- !.
get_tree(b(L,K,D,R),K,D)  :- !.
get_tree(b(L,K0,_,_),K,D) :- K0@>K, !, get_tree(L,K,D).
get_tree(b(_,_,_,R),K,D)  :- !, get_tree(R,K,D).

get_tree(t(_,K,D,_,_,_,_),K,D)	:- !.
get_tree(t(_,_,_,_,K,D,_),K,D)	:- !.
get_tree(t(L,K1,_,_,_,_,_),K,D) :- K1@>K, !, get_tree(L,K,D).
get_tree(t(_,_,_,_,K2,_,R),K,D) :- K@>K2, !, get_tree(R,K,D).
get_tree(t(_,_,_,M,_,_,_),K,D)	:- get_tree(M,K,D).

% update_tree(Tree, Key, Data, New_tree)
%   The search tree Tree, with Data with Key added, is New_tree.
%   If an item with the same key is already there, it is updated.

:- mode update_tree(+,+,?,-).
update_tree(Tree,Key,Data,New) :- ttt_update(Tree,Key,Data,New,_).

% ttt_update(Tree, Key, Data, New_tree, Growth)
%   Arguments are the same as ttt_update/4, except that the last argument
%   "Growth" tells (by 1/0) whether or not the tree has gorwn up.

:- mode ttt_update(+,+,?,-,-).
ttt_update([],K,D,b([],K,D,[]),1) :- !.

ttt_update(b(L,K,_,R),K,D,b(L,K,D,R),0) :- !.
ttt_update(b(L,K0,D0,R),K,D,NT,0) :- K0@>K, !,
    ttt_update(L,K,D,NL,G),
    ( G=:=0, !, NT=b(NL,K0,D0,R);
      NL=b(LL,K1,D1,RR), NT=t(LL,K1,D1,RR,K0,D0,R) ).
ttt_update(b(L,K0,D0,R),K,D,NT,0) :- !,
    ttt_update(R,K,D,NR,G),
    ( G=:=0, !, NT=b(L,K0,D0,NR);
      NR=b(LL,K1,D1,RR), NT=t(L,K0,D0,LL,K1,D1,RR) ).

ttt_update(t(L,K,_,M,KR,DR,R),K,D,t(L,K,D,M,KR,DR,R),0) :- !.
ttt_update(t(L,KL,DL,M,K,_,R),K,D,t(L,KL,DL,M,K,D,R),0) :- !.
ttt_update(t(L,KL,DL,M,KR,DR,R),K,D,NT,G) :- KL@>K, !,
    ttt_update(L,K,D,NL,G),
    ( G=:=0, !, NT=t(NL,KL,DL,M,KR,DR,R);
      NL=b(LL,KLL,DLL,RR), NT=(b(b(LL,KLL,DLL,RR),KL,DL,b(M,KR,DR,R))) ).
ttt_update(t(L,KL,DL,M,KR,DR,R),K,D,NT,G) :- K@>KR, !,
    ttt_update(R,K,D,NR,G),
    ( G=:=0, !, NT=t(L,KL,DL,M,KR,DR,NR);
      NR=b(LL,KRR,DRR,RR), NT=(b(b(L,KL,DL,M),KR,DR,b(LL,KRR,DRR,RR))) ).
ttt_update(t(L,KL,DL,M,KR,DR,R),K,D,NT,G) :- !,
    ttt_update(M,K,D,NM,G),
    ( G=:=0, !, NT=t(L,KL,DL,NM,KR,DR,R);
      NM=b(LL,KM,DM,RR), NT=(b(b(L,KL,DL,LL),KM,DM,b(RR,KR,DR,R))) ).

:- mode intern(+,+,+,-).
intern(Tree,Key,Data,New) :- intern(Tree,Key,Data,New,_).

% intern(Tree, Key, Data, New_tree, Growth)
%   Arguments are the same as intern/4, except that the last argument
%   "Growth" tells (by 1/0) whether or not the tree has gorwn up.

:- mode intern(+,+,+,-,-).
intern([],K,D,b([],K,[D],[]),1) :- !.

intern(b(L,K,D0,R),K,D,b(L,K,[D|D0],R),0) :- !.
intern(b(L,K0,D0,R),K,D,NT,0) :- K0@>K, !,		% 0 replaced by G
    intern(L,K,D,NL,G),
    ( G=:=0, !, NT=b(NL,K0,D0,R);
      NL=b(LL,K1,D1,RR), NT=t(LL,K1,D1,RR,K0,D0,R) ).
intern(b(L,K0,D0,R),K,D,NT,0) :- !,			% 0 replaced by G
    intern(R,K,D,NR,G),
    ( G=:=0, !, NT=b(L,K0,D0,NR);
      NR=b(LL,K1,D1,RR), NT=t(L,K0,D0,LL,K1,D1,RR) ).

intern(t(L,K,D0,M,KR,DR,R),K,D,t(L,K,[D|D0],M,KR,DR,R),0) :- !.
intern(t(L,KL,DL,M,K,D0,R),K,D,t(L,KL,DL,M,K,[D|D0],R),0) :- !.
intern(t(L,KL,DL,M,KR,DR,R),K,D,NT,G) :- KL@>K, !,
    intern(L,K,D,NL,G),
    ( G=:=0, !, NT=t(NL,KL,DL,M,KR,DR,R);
      NL=b(LL,KLL,DLL,RR), NT=(b(b(LL,KLL,DLL,RR),KL,DL,b(M,KR,DR,R))) ).
intern(t(L,KL,DL,M,KR,DR,R),K,D,NT,G) :- K@>KR, !,
    intern(R,K,D,NR,G),
    ( G=:=0, !, NT=t(L,KL,DL,M,KR,DR,NR);
      NR=b(LL,KRR,DRR,RR), NT=(b(b(L,KL,DL,M),KR,DR,b(LL,KRR,DRR,RR))) ).
intern(t(L,KL,DL,M,KR,DR,R),K,D,NT,G) :- !,
    intern(M,K,D,NM,G),
    ( G=:=0, !, NT=t(L,KL,DL,NM,KR,DR,R);
      NM=b(LL,KM,DM,RR), NT=(b(b(L,KL,DL,LL),KM,DM,b(RR,KR,DR,R))) ).

:- mode tree_size(+,-).
tree_size([], 0) :- !.
tree_size(b(L, _, _, R), S) :- !,
    tree_size(L, LS), tree_size(R, RS), S is LS+RS+1.
tree_size(t(L, _, _, M, _, _, R), S) :- !,
    tree_size(L, LS), tree_size(M, MS), tree_size(R, RS), S is LS+MS+RS+2.

:- mode flatten_tree(+,-,+).
flatten_tree([], X, X) :- !.
flatten_tree(b(L,K,D,R), X0, X) :-
    flatten_tree(L, X0, [K,D|X1]),
    flatten_tree(R, X1, X).
flatten_tree(t(L,KL,DL,M,KR,DR,R), X0, X) :-
    flatten_tree(L, X0, [KL,DL|X1]),
    flatten_tree(M, X1, [KR,DR|X2]),
    flatten_tree(R, X2, X).

