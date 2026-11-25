%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% CLAUSE INDEXING

:- mode predicate_dependency(+, -, ?, +).
predicate_dependency([], Cls, Cls, _) :- !.
predicate_dependency([Clause|Clauses], [Clause_table|Cls0], Cls1, Cn) :- 
    convert_one_clause(Clause, (H:-G|B), 0, Nv),
    number_of_registers(Max0), Max is Max0+1,
    array(Max, Head0), functor(H, F, A),
    aset(Head0, 0, F, Head1), 
    initiate_predefined_head(A, H, Head1, Head),
    array(Max, Depend0), 
    aset(Depend0, 0, '$DEPEND', Depend1),
    term_dependency(A, H, G, Depend1, Depend),
    initiate_clause_table((H:-G|B), Head, Depend, Cn, Nv, Clause_table),
    Cn1 is Cn + 1,
    predicate_dependency(Clauses, Cls0, Cls1, Cn1).

:- mode take_apart_clause(+, -, -, -).
take_apart_clause((H:-G|B), H, G, B) :- !.
take_apart_clause((H:-B), H, true, B) :- !.
take_apart_clause(H, H, true, true) :- !.

:- mode initiate_predefined_head(+, +, +, -).
initiate_predefined_head(0, H, Head, Head) :- !.
initiate_predefined_head(A, H, Head0, Head) :-
    arg(A, H, Arg), aset(Head0, A, Arg, Head1),
    A1 is A - 1,
    initiate_predefined_head(A1, H, Head1, Head).

:- mode dependency(+, +, +, -).
dependency(list, One, Guard, list(2,Depend)) :- !,
    arg(1, One, Car), kl1_type_of(Car, CarType),
    dependency(CarType, Car, Guard, CarDepend), 
    arg(2, One, Cdr), kl1_type_of(Cdr, CdrType),
    dependency(CdrType, Cdr, Guard, CdrDepend), 
    array(3, Depend0), 
    aset(Depend0, 0, '$LIST', Depend1),
    aset(Depend1, 1, CarDepend, Depend2),
    aset(Depend2, 2, CdrDepend, Depend).
%dependency(nil, _, _, list(0,[])) :- !.          % 88.09.12 Y.Kimura
dependency(nil, Arg, _, atom(Arg)) :- !.         
dependency(integer,  Arg, _, integer(Arg)) :- !.
dependency(float,  Arg, _, float(Arg)) :- !.	% 890404 Nishizaki
dependency(atom, Arg, _, atom(Arg)) :- !.
dependency(var, Arg, Guard, var(Depend,Arg)) :- !,
    guard_variable_check(Guard, Arg, Depend).
dependency(string(Type), Arg, _, string(Type,Arg)) :- !.
dependency(vector(A), Arg, Guard, vector(A,Depend)) :- !,
    A1 is A+1, 
    array(A1, Depend0), aset(Depend0, 0, '$VECT', Depend1),
    term_dependency(A, Arg, Guard, Depend1, Depend).

:- mode term_dependency(+, +, +, +, -).
term_dependency(0, Vect, Guard, Depend, Depend) :- !.
term_dependency(A, Vect, Guard, Depend0, Depend) :- 
    arg(A, Vect, E),
    kl1_type_of(E, Type),
    dependency(Type, E, Guard, OneDepend),
    aset(Depend0, A, OneDepend, Depend1),
    A1 is A-1,
    term_dependency(A1, Vect, Guard, Depend1, Depend).

:- mode guard_variable_check(+, +, -).
guard_variable_check(true, Arg, var) :- !.
guard_variable_check((Blt, Tail), Arg, Depend) :- !,
  ( guard_variable_check(Blt, Arg, Depend), Depend \== var, !;
    guard_variable_check(Tail, Arg, Depend), Depend \== var, !;
    Depend = var ).
guard_variable_check(Arg=Y, Arg, Depend) :- !, 
    kl1_type_of(Y, Depend).
guard_variable_check(X=Arg, Arg, Depend) :- !, 
    kl1_type_of(X, Depend).
guard_variable_check(X=Y, Arg, var) :- !.
guard_variable_check(':='(X, Y), Arg, Depend) :- !, 
    guard_variable_check(Y, Arg, Depend).
guard_variable_check(Blt, Arg, Depend) :- 
    builtin(Blt, _, _, _, Attr, _, _), !,
    builtin_arg_dependency(Attr, Arg, Depend).
guard_variable_check(X, _, var).	% 890703 Nishizaki: Bad Guard Goal

:- mode builtin_arg_dependency(+, +, -).
builtin_arg_dependency([], Arg, var) :- !.
builtin_arg_dependency([(Arg,Type)|_], Arg, Type) :- !.
builtin_arg_dependency([_|Tail], Arg, Depend) :- !,
    builtin_arg_dependency(Tail, Arg, Depend).

%%%% Making indexed tree

:- mode make_indexed_tree(+, +, +, -).
make_indexed_tree([], _, _, []) :- !.
make_indexed_tree([Cls0], [], Reg0, leaf(Cls2)) :- is_clause(Cls0), !,
    Reg1 is Reg0-1,
    reconstruct_one_clause(Cls0, Reg1, Cls2).
make_indexed_tree(Clses, [], Reg, Guard) :-
    Reg1 is Reg - 1, 
    is_head_structure_really_same(Reg1, Clses), !,
    create_guard_tables(Clses, Reg, []-TbyG, []-TbyI, []-TbyV, []-Next0),
    sort(Next0, Next),
    initiate_clause_tree(Clses, TbyC),
    make_indexed_tree_by_guard(Next, TbyC, Reg, TbyG-TbyI-TbyV, Guard).
make_indexed_tree(Clses, [], Reg, Try) :- !,
    Reg1 is Reg-1,
    reconstruct_clauses(Clses, Reg1, Try, []).
make_indexed_tree(Clses0, [In0|Next], Reg0, nonvar(Expand,Nonvar,Var)) :- 
    decide_indexing_arg(In0, In, Reg0, Reg, Expand, Clses0, Clses), 
    set_type_tree(Clses, 	In,
		  []-Atomt,	[]-Intt,
		  []-Listt,	[]-Vectt,
		  []-Strgt,	[]-Elset,
		  []-Waitt,     []-Uvart),
    classify_nonvar_clses(Atomt, Intt, Listt, Vectt, Strgt, Elset, Waitt,
			  Next, In, Reg, Nonvar),
    classify_var_clses(Uvart, Next, In, Reg, Var).

:- mode decide_indexing_arg(+, -, +, -, -, +, -). 
decide_indexing_arg(In, In, Reg, Reg, In, Cls, Cls) :- integer(In), !.
decide_indexing_arg(In, Reg, Reg, Reg, In, Cls, Cls) :-	% 900522 Nishizaki
    number_of_registers(RMax), Reg > RMax,
    error('Unification too much complicated'), !.
decide_indexing_arg(car(In), Reg0, Reg0, Reg1, car(In,Reg0), 
                                               Clses0, Clses) :- !,
    Reg1 is Reg0 + 1,
    expand_structure_args(Clses0, In, Reg0, 1, Clses).
decide_indexing_arg(cdr(In), Reg0, Reg0, Reg1, cdr(In,Reg0), 
                                               Clses0, Clses) :- !,
    Reg1 is Reg0 + 1,
    expand_structure_args(Clses0, In, Reg0, 2, Clses).
decide_indexing_arg(element(In,Index), Reg0, Reg0, Reg1, 
	            element(In,Index,Reg0), Clses0, Clses) :- !,
    Reg1 is Reg0 + 1, Index1 is Index+1,
    expand_structure_args(Clses0, In, Reg0, Index1, Clses).

:- mode set_type_tree(+, +, +, +, +, +, +, +, +, +).
set_type_tree([], _, At-At, It-It, 
	             Lt-Lt, Vt-Vt, 
		     St-St, Et-Et, 
                     Wt-Wt, Ut-Ut) :- !.
set_type_tree([Cls|Cdr],In,
	      At0-At2, 	It0-It2, 
	      Lt0-Lt2, 	Vt0-Vt2, 
	      St0-St2, 	Et0-Et2,
	      Wt0-Wt2,  Ut0-Ut2) :-
    find_key(Cls, In, Type, Key),
    intern_clause(Type, Key, Cls, 
	          At0-At1, It0-It1, 
	          Lt0-Lt1, Vt0-Vt1, 
	          St0-St1, Et0-Et1,
		  Wt0-Wt1, Ut0-Ut1),
    set_type_tree(Cdr,     In,
		  At1-At2, It1-It2, 
		  Lt1-Lt2, Vt1-Vt2, 
		  St1-St2, Et1-Et2,
		  Wt1-Wt2, Ut1-Ut2).

:- mode find_key(+, +, -, -).
find_key(Clause, In, Type, Key) :- 
    get_clause_dependency(Clause, Depend),
    aref(Depend, In, X), type_key(X, Type, Key).
     
:- mode type_key(+, -, -).
type_key(integer(Int),	  integer, integer(Int)) :- !.
type_key(float(Float),	  float,   float(Float)) :- !.	% 890404 Nishizaki
type_key(atom(A),	  atom,    atom(A)     ) :- !.
type_key(string(Key,_),   string,  string      ) :- !.
type_key(list(Arity,_),   list,    Arity       ) :- !.
type_key(vector(Arity,_), vector,  Arity       ) :- !.
type_key(var((wait),_),   (wait),  (wait)      ) :- !.		
type_key(var(var,_),      var,     var         ) :- !.
type_key(var(Type,_),     Key,     type(Key)   ) :- !, 
    functor(Type, Key, _).
type_key(Type,            else,    Type        ) :- !.

:- mode intern_clause(+, +, +, +, +, +, +, +, +, +, +).
intern_clause(var, Key, Cls, A-A, I-I, L-L, V-V, S-S, E-E, W-W, Ut0-Ut1) :- !, 
     intern(Ut0, Key, Cls, Ut1).
intern_clause((wait), Key, Cls, A-A, I-I, L-L, V-V, S-S, E-E, 
                                                    W0-W1, U-U) :- !, 
     intern(W0, Key, Cls, W1).
intern_clause(list, Key, Cls, A-A, I-I, Lt0-Lt1, V-V, S-S, E-E, 
                                                      W-W, U-U) :- !,
     intern(Lt0, Key, Cls, Lt1).
intern_clause(integer, Key, Cls, A-A, It0-It2, L-L, V-V, S-S, E-E, 
                                                         W-W, U-U) :- !,
     intern(It0, Key, Cls, It1), intern_key(It1, Key, It2).
intern_clause(float, Key, Cls, A-A, It-It, L-L, V-V, S-S, Et0-Et2, % Nishizaki
                                                         W-W, U-U) :- !,
     intern(Et0, Key, Cls, Et1), intern_key(Et1, Key, Et2).
intern_clause(atom, Key, Cls, At0-At2, I-I, L-L, V-V, S-S, E-E, W-W, U-U) :- !,
     intern(At0, Key, Cls, At1), intern_key(At1, Key, At2).
intern_clause(string, Key, Cls, A-A, I-I, L-L, V-V, St0-St2, E-E, 
                                                    W-W, U-U) :- !,
     intern(St0, Key, Cls, St1), intern_key(St1, Key, St2).
intern_clause(vector, Key, Cls, A-A, I-I, L-L, Vt0-Vt2, S-S, E-E,
                                                        W-W, U-U) :- !,
     intern(Vt0, Key, Cls, Vt1), intern_key(Vt1, Key, Vt2).
intern_clause(else, Key, Cls, A-A, I-I, L-L, V-V, S-S, Et0-Et2,
                                                       W-W, U-U) :- !,
     intern(Et0, Key, Cls, Et1), intern_key(Et1, Key, Et2).

:- mode intern_key(+, +, -).
intern_key(T0, Key, T1) :- !, intern(T0, '$KEY', Key, T1).

:- mode get_key(+, -).
get_key(Tree, Key) :- get_tree(Tree, '$KEY', Key).


%%%%% Classification of nonvar clauses

:- mode classify_nonvar_clses(+, +, +, +, +, +, +, +, +, +, -).
classify_nonvar_clses([], [], [], [], [], [], [], _, _, _, []) :- !. 
classify_nonvar_clses(Atomt, Intt, Listt, Vectt, Strgt, Elset, Waitt, 
		      Next, In, RegN,
		      wait(In, Type, Wait)) :- 
    classify_typed_clses(Atomt, Intt, Listt, Vectt, Strgt, Elset,
                         Next, In, RegN, Type),
    classify_wait_clses(Waitt, Next, In, RegN, Wait).

:- mode classify_typed_clses(+, +, +, +, +, +, +, +, +, -).
classify_typed_clses([], [], [], [], [], [], _, _, _, []) :- !.
classify_typed_clses(Atomt, Intt, Listt, Vectt, Strgt, Elset, Next, In, RegN,
		     type(In, Att, Itt, Ltt, Vtt, Stt, Ett)) :- 
    get_key(Atomt, Akey0), sort(Akey0, AkeyT), 
    sort_1(AkeyT, Akey),
    classify_atom(Akey, Atomt, Next, In, RegN, Att),
    get_key(Intt, Ikey0), sort(Ikey0, IkeyT),
    sort_1(IkeyT, Ikey),
    classify_integer(Ikey, Intt, Next, In, RegN, Itt),
    classify_lists(Listt, Next, In, RegN, Ltt),
    get_key(Vectt, Vkey0), sort(Vkey0, VkeyT),
    sort_1(VkeyT, Vkey),
    classify_vectors(Vkey, Vectt, Next, In, RegN, Vtt),
    get_key(Strgt, Skey0), sort(Skey0, Skey1),
    sort_1(Skey1, Skey),
    classify_strings(Skey, Strgt, Next, In, RegN, Stt),
    get_key(Elset, Ekey0), sort(Ekey0, Ekey1),
    sort_1(Ekey1, Ekey),
    classify_else_type(Ekey, Elset, Next, In, RegN, Ett).

%%%%% Classification of each types
%%%%% Atoms or integers

:- mode classify_atom(+, +, +, +, +, -).
classify_atom([], _, _, _, _, []) :- !.
classify_atom(Key, Tree, Next, In, RegN, atom(In, Const, Type)) :-
    create_atomic_node(Key, Tree, Next, In, RegN, Const-[], Type-[]).

:- mode classify_integer(+, +, +, +, +, -).
classify_integer([], _, _, _, _, []) :- !.
classify_integer(Key, Tree, Next, In, RegN, integer(In, Const, Type)) :-
    create_atomic_node(Key, Tree, Next, In, RegN, Const-[], Type-[]).

:- mode create_atomic_node(+, +, +, +, +, +, +).
create_atomic_node([], _, _, _, _, C-C, T-T) :- !.
create_atomic_node([type(atom)|Keys], Tree, Next, In, Reg, A0A1, T0-T2) :-
    get_tree(Tree, type(atom), Clauses),
    create_type_node(Clauses, atom, Next, In, Reg, T0, T1),
    create_atomic_node(Keys, Tree, Next, In, Reg, A0A1, T1-T2).
create_atomic_node([type(integer)|Keys], Tree, Next, In, Reg, A0A1, T0-T2) :-
    get_tree(Tree, type(integer), Clauses),
    create_type_node(Clauses, integer, Next, In, Reg, T0, T1),
    create_atomic_node(Keys, Tree, Next, In, Reg, A0A1, T1-T2).
create_atomic_node([type(float)|Keys], Tree, Next, In, Reg, A0A1, T0-T2) :-
    get_tree(Tree, type(float), Clauses),	% 890404 Nishizaki
    create_type_node(Clauses, float, Next, In, Reg, T0, T1),
    create_atomic_node(Keys, Tree, Next, In, Reg, A0A1, T1-T2).
create_atomic_node([Akey|Keys], Tree, Next, In, Reg, A0-A2, T0T1) :-
    get_tree(Tree, Akey, Clauses),
    create_switch_node(Clauses, Akey, Next, In, Reg, A0, A1),
    create_atomic_node(Keys, Tree, Next, In, Reg, A1-A2, T0T1).

:- mode create_type_node(+, +, +, +, +, -, ?).
create_type_node([One0], Type, Next, In, Reg0, [(Type,leaf(New))|A], A) :- !,
    update_predefined_arg([One0], In, '$TYPE'(Type), [One1]),
    Reg1 is Reg0-1,
    reconstruct_one_clause(One1, Reg1, New).
create_type_node(Clauses0, Type, Next, In, Reg, [(Type,Res)|A], A) :- !,
    update_predefined_arg(Clauses0, In, '$TYPE'(Type), Clauses1),
    make_indexed_tree(Clauses1, Next, Reg, Res).

:- mode create_switch_node(+, +, +, +, +, -, ?).
create_switch_node([One0], Key, Next, In, Reg0, [(Key,leaf(New))|A], A) :- !,
    update_predefined_arg([One0], In, '$VOID', [One1]),
    Reg1 is Reg0-1,
    reconstruct_one_clause(One1, Reg1, New).
create_switch_node(Clauses0, Key, Next, In, Reg, [(Key,Res)|A], A) :- !,
    update_predefined_arg(Clauses0, In, '$VOID', Clauses1),
    make_indexed_tree(Clauses1, Next, Reg, Res).
    
%%%%% Lists

:- mode classify_lists(+, +, +, +, -).
classify_lists([], _, _, _, []) :- !.
classify_lists(Listt, Next, In, Reg, list(In, Cons)) :-
    get_tree(Listt, 2, ConsClses),
    get_tree(Listt, type(list), TypeClses),
    classify_cons_node(ConsClses, TypeClses, Next, In, Reg, Cons).
%    get_tree(Listt, 0, NilClses),
%    update_predefined_arg(NilClses, In, '$VOID', NewNil),
%    make_indexed_tree(NewNil, Next, Reg, Nil).

:- mode create_cons_node(+, +, +, +, +, -).
classify_cons_node([], [], Next, In, Reg, []) :- !.
classify_cons_node(ConsClses, TypeClses, Next, In, Reg, 
                                         cons(ListNode,TypeNode)) :-
    create_list_node(ConsClses, Next, In, Reg, ListNode),
    update_predefined_arg(TypeClses, In, '$TYPE'(list), NewTypeClses),
    make_indexed_tree(NewTypeClses, Next, Reg, TypeNode).

:- mode create_list_node(+, +, +, +, -).
create_list_node([], _, _, _, []) :- !.
create_list_node([One0], _, In, Reg0, leaf(New)) :- !,
    update_predefined_arg([One0], In, '$LIST', [One1]),
    Reg1 is Reg0-1,
    reconstruct_one_clause(One1, Reg1, New).
create_list_node(Clauses0, Next, In, Reg, Ltree) :-
    update_predefined_arg(Clauses0, In, '$LIST', Clauses1),
    make_indexed_tree(Clauses1, [car(In),cdr(In)|Next], Reg, Ltree).    

%%%%% Vectors

:- mode classify_vectors(+, +, +, +, +, -).
classify_vectors([], _, _, _, _, []) :- !.
classify_vectors(Vkey, Vectt, Next, In, Reg, vector(In, Vect, VType)) :-
    create_vector_node(Vkey, Vectt, Next, In, Reg, Vect-[], VType-[]).

:- mode create_vector_node(+, +, +, +, +, +, +).
create_vector_node([], _, _, _, _, I-I, T-T) :- !.
create_vector_node([type(vector)|Vkeys], Vtt, Next, In, Reg, I0I1, 
					      [(vector,Res)|T0]-T1) :- !,
    get_tree(Vtt, type(vector), Clauses0),
    update_predefined_arg(Clauses0, In, '$TYPE'(vector), Clauses1),
    make_indexed_tree(Clauses1, Next, Reg, Res),
    create_vector_node(Vkeys, Vtt, Next, In, Reg, I0I1, T0-T1).
create_vector_node([Vkey|Vkeys], Vtt, Next, In, Reg, I0-I2, T0T1) :-
    get_tree(Vtt, Vkey, Clauses),
    create_arity_node(Clauses, Vkey, Next, In, Reg, I0, I1),
    create_vector_node(Vkeys, Vtt, Next, In, Reg, I1-I2, T0T1).

:- mode create_arity_node(+, +, +, +, +, -, ?).
create_arity_node([One0], Vkey, _, In, Reg0, [(Vkey,leaf(New))|A], A) :- !,
    update_predefined_arg([One0], In, '$VECT', [One1]),
    Reg1 is Reg0-1,
    reconstruct_one_clause(One1, Reg1, New).
create_arity_node(Clauses0, Vkey, Next, In, Reg, [(Vkey,Res)|A], A) :- !,
    update_predefined_arg(Clauses0, In, '$VECT', Clauses1),
    create_indexed_vector_arg_list(Vkey, In, Next, NewNext),
    make_indexed_tree(Clauses1, NewNext, Reg, Res).

:- mode create_indexed_vector_arg_list(+, +, +, -).
create_indexed_vector_arg_list(0, _, Next, Next) :- !.
create_indexed_vector_arg_list(E, In, Next, NewNext) :- !,
    E1 is E - 1,
    create_indexed_vector_arg_list(E1, In, [element(In,E1)|Next], NewNext).

%%%%% Strings    

:- mode classify_strings(+, +, +, +, +, -).
classify_strings([], _, _, _, _, []) :- !.
classify_strings(Skey, Strgt, Next, In, Reg, string(In, Strg, SType)) :-
    create_string_node(Skey, Strgt, Next, In, Reg, Strg-[], []-SType).

:- mode create_string_node(+, +, +, +, +, +, +).
create_string_node([], _, _, _, _, I-I, T-T) :- !.
create_string_node([type(string)|Skeys], Strgt, Next, In, Reg, I0I1, 
					                  _-Type) :- !,
    get_tree(Strgt, type(string), Clauses0),
    update_predefined_arg(Clauses0, In, '$TYPE'(string), Clauses1),
    make_indexed_tree(Clauses1, Next, Reg, Res),
    create_string_node(Skeys, Strgt, Next, In, Reg, I0I1, Res-Type).
create_string_node([Skey|Skeys], Strgt, Next, In, Reg, [One|I0]-I1, TYPE) :-
    get_tree(Strgt, Skey, Clauses),
    create_one_string_node(Clauses, Next, Reg, One),
    create_string_node(Skeys, Strgt, Next, In, Reg, I0-I1, TYPE).

:- mode create_one_string_node(+, +, +, -).
create_one_string_node([Cls], Next, Reg0, leaf(NewCls)) :- !,
    Reg1 is Reg0-1,
    reconstruct_one_clause(Cls, Reg1, NewCls).
create_one_string_node(Clses, Next, RegN, Tree) :- !,
    make_indexed_tree(Clses, Next, RegN, Tree).


%%%%% Other types (Float, Code, Module, etc)

:- mode classify_else_type(+, +, +, +, +, -).
classify_else_type([], _, _, _, _, []) :- !.
classify_else_type(Key, Tree, Next, In, RegN, float(In, Const, Type)) :-
    Key = [float(_)|_],			% 890404 Nishizaki
    create_atomic_node(Key, Tree, Next, In, RegN, Const-[], Type-[]).
classify_else_type(Key, Tree, Next, In, RegN, float(In, Const, Type)) :-
    Key = [type(float)|_],		% 890404 Nishizaki
    create_atomic_node(Key, Tree, Next, In, RegN, Const-[], Type-[]).
classify_else_type(Ekey, Elset, Next, In, Reg, else(In, Else)) :- 
    create_else_node(Ekey, Elset, Next, In, Reg, Else-[]).

:- mode create_else_node(+, +, +, +, +, +).
create_else_node([], _, _, _, _, I-I) :- !.
create_else_node([Ekey|Ekeys], Elset, Next, In, Reg, [One|I0]-I1) :-
    get_tree(Elset, Ekey, Clauses),
    create_one_else_node(Clauses, Next, Reg, One),
    create_else_node(Ekeys, Elset, Next, In, Reg, I0-I1).

:- mode create_one_else_node(+, +, +, -).
create_one_else_node(Clauses, Next, Reg, Tree) :-
    create_one_string_node(Clauses, Next, Reg, Tree).


%%%%% Instantiated Variables

:- mode classify_wait_clses(+, +, +, +, -).
classify_wait_clses([], _, _, _, []) :- !.
classify_wait_clses(Waitt, Next, In, Reg, Wait) :-
    get_tree(Waitt, (wait), WList0),
    update_predefined_arg(WList0, In, '$WAIT', WList1),
    make_indexed_tree(WList1, Next, Reg, Wait).

%%%%% Variables

:- mode classify_var_clses(+, +, +, +, -).
classify_var_clses([], Next, In, Reg, []) :- !.
classify_var_clses(Uvart, Next, In, Reg, Any) :- 
    get_tree(Uvart, var, AList),
    make_indexed_tree(AList, Next, Reg, Any).


%%%%% Expand structure arguments

:- mode update_predefined_arg(+, +, +, -).
update_predefined_arg([Cls0|Clauses0], In, Type, [Cls1|Clauses1]) :- !,
    get_predefined_head(Cls0, Head0),
    aref(Head0, In, Arg),
    aset(Head0, In, Type@Arg, Head1),
    update_predefined_head(Cls0, Head1, Cls1),
    update_predefined_arg(Clauses0, In, Type, Clauses1).
update_predefined_arg([], _, _, []) :- !.

:- mode expand_structure_args(+, +, +, +, -).
expand_structure_args([Cls0|Clses0], In, Reg, Index, [Cls|Clses]) :-
    update_dependency(Cls0, In, Reg, Index, Cls1),
    update_head_struct_arg(Cls1, In, Reg, Index, Cls),
    expand_structure_args(Clses0, In, Reg, Index, Clses).
expand_structure_args([], _, _, _, []) :- !.

:- mode update_dependency(+, +, +, +, -).
update_dependency(Cls0, In, Reg, Index, Cls1) :- 
    get_clause_dependency(Cls0, Depend0),
    aref(Depend0, In, ArgDepend), arg(2, ArgDepend, DependArray),
    aref(DependArray, Index, ElementDepend),
    aset(Depend0, Reg, ElementDepend, Depend1),
    update_clause_dependency(Cls0, Depend1, Cls1).

:- mode update_head_struct_arg(+, +, +, +, -).
update_head_struct_arg(Cls0, In, Reg, Index, Cls1) :-
    get_predefined_head(Cls0, Head0),
    aref(Head0, In, StructData), 
    reconstruct_struct_arg(StructData, Index, ExpandedElem, NewData),
    aset(Head0, In, NewData, Head1),
    aset(Head1, Reg, ExpandedElem, Head2),
    update_predefined_head(Cls0, Head2, Cls1).

:- mode reconstruct_struct_arg(+, +, -, -).
reconstruct_struct_arg(Type@StructData, Index, ExpandedElem, Type@NewData) :- 
    is_indexing_flag(Type), !,
    reconstruct_struct_arg(StructData, Index, ExpandedElem, NewData).
reconstruct_struct_arg(StructData, Index, ExpandedElem, NewData) :- 
    convert_data_into_inner_data(StructData, InnData),
    aref(InnData, Index, ExpandedElem),
    aset(InnData, Index, '$VOID'@ExpandedElem, NewData).

:- mode is_indexing_flag(+).
is_indexing_flag('$VOID') :- !.
is_indexing_flag('$LIST') :- !.
is_indexing_flag('$VECT') :- !.
is_indexing_flag('$WAIT') :- !.
is_indexing_flag('$TYPE'(_)) :- !.

:- mode convert_data_into_inner_data(+, -).
convert_data_into_inner_data(StructData, StructData) :- 
    functor(StructData, '$array', _), !.
convert_data_into_inner_data(StructData, NewData) :- 
    functor(StructData, F, A),
  ( F == '$LIST', ! ; F == '$VECT' ),
    A1 is A+1,
    array(A1, Array0), aset(Array0, 0, F, Array1),
    copy_args_into_inner_structure(A, StructData, Array1, NewData).

:- mode copy_args_into_inner_structure(+, +, +, -).
copy_args_into_inner_structure(0, _, NewData, NewData) :- !.
copy_args_into_inner_structure(A, StructData, Array0, NewData) :-
    arg(A, StructData, Element),
    aset(Array0, A, Element, Array1),
    A1 is A-1,
    copy_args_into_inner_structure(A1, StructData, Array1, NewData).

:- mode make_index_arg_list(+, +, -, ?).
make_index_arg_list(T, T, [T|L], L) :- !.
make_index_arg_list(F, T, L, L) :- F > T, !.
make_index_arg_list(F, T, [F|L0], L1) :- F < T, !, F1 is F+1, 
     make_index_arg_list(F1, T, L0, L1).

%%%%% Making indexed tree by guard builtin predicates

:- mode is_head_structure_really_same(+, +).
is_head_structure_really_same(0, _) :- !.
is_head_structure_really_same(Reg, Clses) :- !,
    is_head_structure_really_same_1(Clses, Reg, Res0, []),
    sort(Res0, Res1), sort_1(Res1, Res),
    Res = [(_,_)], Reg1 is Reg - 1,
    is_head_structure_really_same(Reg1, Clses).

:- mode is_head_structure_really_same_1(+, +, -, ?).
is_head_structure_really_same_1([One|Clses], Reg, 
                                [(Var,Attr)|Res0], Res1) :- !,
    get_predefined_head(One, H),
    get_clause_dependency(One, Depend),
    aref(H, Reg, E0), kl1_var_or_derefed(E0, Var),
    aref(Depend, Reg, D0), arg(1, D0, Attr),
    is_head_structure_really_same_1(Clses, Reg, Res0, Res1).
is_head_structure_really_same_1([], _, Res, Res) :- !.

:- mode create_guard_tables(+, +, +, +, +, +).
create_guard_tables([], _, TbyG-TbyG, TbyI-TbyI, TbyV-TbyV, Next-Next) :- !.
create_guard_tables([One|Clses], Reg, TbyG0-TbyG2, 
	                              TbyI0-TbyI2,
	                              TbyV0-TbyV2,
				      Next0-Next2) :- 
    process_one_guard(One, Reg, TbyG0-TbyG1, 
                                TbyI0-TbyI1, 
				TbyV0-TbyV1,
				Next0-Next1), !,
    create_guard_tables(Clses, Reg, TbyG1-TbyG2, 
                                    TbyI1-TbyI2, 
				    TbyV1-TbyV2,
				    Next1-Next2).

:- mode process_one_guard(+, +, +, +, +, +).
process_one_guard(Clause, Reg, TBYG, TbyI0-TbyI2, TBYV, Next0-Next1) :-
    get_clause_no(Clause, Cn),
    get_original_clause(Clause, Cls), take_apart_clause(Cls, _, G, _),
    process_guard_goals(G, TBYG, TbyI0-TbyI1, 0-I, Cn),
    update_guard_table(TbyI1, '$NUMBER_OF_GUARDS'(Cn), I, TbyI2),
    generate_next_guard_pos_list(I, Cn, Next0, Next1),
    get_predefined_head(Clause, H),
    get_clause_dependency(Clause, Depend),
    Reg1 is Reg-1,
    process_predefined_head_args(Reg1, H, Depend, TBYV).

:- mode process_guard_goals(+, +, +, +, +).
process_guard_goals(true, TbyG-TbyG, TbyI-TbyI, I-I, _) :- !.
process_guard_goals((A,B), TbyG0-TbyG2, TbyI0-TbyI2, I0-I2, Cn) :- !,
    process_guard_goals(A, TbyG0-TbyG1, TbyI0-TbyI1, I0-I1, Cn),
    process_guard_goals(B, TbyG1-TbyG2, TbyI1-TbyI2, I1-I2, Cn).
process_guard_goals(G, TbyG0-TbyG1, TbyI0-TbyI1, I0-I1, Cn) :- !,
    I1 is I0+1,
    intern_guard_table(TbyG0, G,       (Cn,I1), TbyG1),
    update_guard_table(TbyI0, (Cn,I1), G,       TbyI1).

:- mode generate_next_guard_pos_list(+, +, +, -).
generate_next_guard_pos_list(0, _, Next, Next) :- !.
generate_next_guard_pos_list(I, Cn, Next0, Next) :-
    I1 is I-1,
    generate_next_guard_pos_list(I1, Cn, [(Cn,I)|Next0], Next).

:- mode process_predefined_head_args(+, +, +, +).
process_predefined_head_args(0, _, _, TbyV-TbyV) :- !.
process_predefined_head_args(Reg, H, Depend, TbyV0-TbyV3) :- 
    aref(H, Reg, E), 
  ( kl1_var_or_derefed(E, NewE), !,
	update_guard_table(TbyV0, NewE, Reg, TbyV1),
    	aref(Depend, Reg, One), arg(1, One, Atype),     % One is of the form
	                                                %   var(Type, V).
	update_guard_table(TbyV1, '$TYPE'(Reg), Atype, TbyV2) ;
      TbyV2 = TbyV0 ),
    Reg1 is Reg - 1,
%    display('process_predefined_head_args  '), 
%    display('Reg = '), display(Reg), ttynl,
%    debug_display_tree(TbyV2), 
    process_predefined_head_args(Reg1, H, Depend, TbyV2-TbyV3).

:- mode kl1_var_or_derefed(+, -).
kl1_var_or_derefed(Flag@E, E) :- is_indexing_flag(Flag), !.
kl1_var_or_derefed(E, E) :- kl1_var(E), !.

:- mode initiate_clause_tree(+, -).
initiate_clause_tree(Clses, TbyC) :- 
    initiate_clause_tree_1(Clses, [], TbyC0, Key0, []),
    sort(Key0, KeyT), sort_1(KeyT, Key),
    update_guard_table(TbyC0, '$CLAUSE_NO_LIST', Key, TbyC).

:- mode initiate_clause_tree_1(+, +, -, -, ?).
initiate_clause_tree_1([], TbyC, TbyC, Key, Key) :- !.
initiate_clause_tree_1([One|Clses], TbyC0, TbyC2, [Cn|Key0], Key1) :-
    get_clause_no(One, Cn),
    update_guard_table(TbyC0, Cn, One, TbyC1),
    initiate_clause_tree_1(Clses, TbyC1, TbyC2, Key0, Key1).

%%%%% Making an indexed tree by guard builtin predicates

:- mode make_indexed_tree_by_guard(+, +, +, +, -).
make_indexed_tree_by_guard(Next, TbyC, Reg0, TbyG0-TbyI0-TbyV0,
	                   guard(BltList, 
                                 blt(CommonNode, RevoltNode),
				 UnmatchedNode)) :-
    get_next_indexing_guard(Next, NewNext, Blt, 
                            TbyC, TbyG0-TbyI0, 
                            ComPosL, ComCnL,
			    RevPosL, RevCnL,
			    UnmatchedL),
    classify_guard_goal(ComCnL,   RevCnL,   UnmatchedL,
                        CommonT0, RevoltT, UnmatchedT,
                        TbyC),
    lift_up_builtin_args(Blt, BltList, Reg0-Reg1, TbyV0-TbyV1, RegVarPair),
    update_predefined_reg_list(RegVarPair, TbyV1, TbyV2),    
    modify_common_clauses(ComPosL, RegVarPair, TbyI0-TbyI1, CommonT0-CommonT),
    modify_revolt_clauses(RevPosL, TbyI1-TbyI2),
    pick_up_next_clause_list_from(ComCnL, NewNext, ComNext, []),
    make_indexed_tree_by_guard(ComNext, CommonT, Reg1,
                               TbyG0-TbyI2-TbyV2, CommonNode),
    pick_up_next_clause_list_from(RevCnL, NewNext, RevNext, []),
    make_indexed_tree_by_guard(RevNext, RevoltT, Reg1, 
                               TbyG0-TbyI2-TbyV2, RevoltNode),
    drop_classified_clause(NewNext, ComCnL, RevCnL, UnmatchedNext),
    make_indexed_tree_by_guard(UnmatchedNext, UnmatchedT, Reg0,
                               TbyG0-TbyI2-TbyV0, UnmatchedNode).
make_indexed_tree_by_guard(_, TbyC, Reg0, TABLE, Clses) :- !,
    refer_guard_table(TbyC, '$CLAUSE_NO_LIST', CList),
    Reg is Reg0-1,
    convert_clause_tree_to_list(CList, TbyC, Reg, TABLE, Clses, []).

:- mode pick_up_next_clause_list_from(+, +, -, ?).
pick_up_next_clause_list_from([], _, NewNext, NewNext) :- !.
pick_up_next_clause_list_from([One|CnL], Next0, NewNext0, NewNext2) :-
    pick_up_one_clause(Next0, One, Next1, NewNext0, NewNext1),
    pick_up_next_clause_list_from(CnL, Next1, NewNext1, NewNext2).

:- mode pick_up_one_clause(+, +, -, -, ?).
pick_up_one_clause([], One, [], NewNext, NewNext) :- !.
pick_up_one_clause([(X,Y)|Next0], X, Next1, [(X,Y)|NewNext0], NewNext1) :-
    pick_up_one_clause(Next0, X, Next1, NewNext0, NewNext1).
pick_up_one_clause([(X,Y)|Next0], One, Next1, NewNext0, NewNext1) :-
    X < One, !,
    pick_up_one_clause(Next0, One, Next1, NewNext0, NewNext1).
pick_up_one_clause([_|Next], One, Next, NewNext, NewNext) :- !.

:- mode drop_classified_clause(+, +, +, -).
drop_classified_clause(Next, ComCnL, RevCnL, UnmatchedNext) :-
    drop_pos_list_of(ComCnL, Next, NewNext0, []),
    drop_pos_list_of(RevCnL, NewNext0, NewNext1, []),
    sort(NewNext1, UnmatchedNext).

:- mode drop_pos_list_of(+, +, -, ?).
drop_pos_list_of([], _, NewNext, NewNext) :- !.
drop_pos_list_of([One|CnL], Next0, NewNext0, NewNext2) :-
    drop_one_clause(Next0, One, Next1, NewNext0, NewNext1),
    drop_pos_list_of(CnL, Next1, NewNext1, NewNext2).

:- mode drop_one_clause(+, +, -, -, ?).
drop_one_clause([], _, [], NewNext, NewNext) :- !.
drop_one_clause([(X,Y)|Next0], X, Next1, NewNext0, NewNext1) :-
    drop_one_clause(Next0, X, Next1, NewNext0, NewNext1).
drop_one_clause([(X,Y)|Next0], One, Next1, [(X,Y)|NewNext0], NewNext1) :-
    X < One, !,
    drop_one_clause(Next0, One, Next1, NewNext0, NewNext1).
drop_one_clause([_|Next], One, Next, NewNext, NewNext) :- !.

:- mode get_next_indexing_guard(+, -, -, +, +, -, -, -, -, -).
get_next_indexing_guard([], [], [], _, _, [], [], [], [], []) :- !, fail.
get_next_indexing_guard([Pos|Next], Next, Blt, TbyC, TbyG-TbyI, 
                                               ComPosL, ComCnL,
					       RevPosL, RevCnL,
					       UnmatchedL) :-
    refer_guard_table(TbyI, Pos, Blt), 
    Blt \== true, 
    functor(Blt, F, A), F \== vector_element,      %%%%% 881011 Y.Kimura 
    builtin(Blt, _, _, _, _, _, _),
    exists_common_or_revolt_pattern(Blt, ComPosL, RevPosL, TbyG), !,
    refer_guard_table(TbyC, '$CLAUSE_NO_LIST', CnL),
    divide_clause_list_with(CnL, ComPosL, RevPosL, UnmatchedL, []),
    extract_CnL_from_pos_list(ComPosL, ComCnL, []),
    extract_CnL_from_pos_list(RevPosL, RevCnL, []).
%get_next_indexing_guard([_|Next], NewNext, Blt, TbyC, TbyGTbyI, % 890912
%                                               ComPosL, ComCnL, % Nishizaki
%					       RevPosL, RevCnL,
%					       UnmatchedL) :-
%    get_next_indexing_guard(Next, NewNext, Blt, TbyC, TbyGTbyI, 
%                                               ComPosL, ComCnL,
%					       RevPosL, RevCnL,
%					       UnmatchedL).
get_next_indexing_guard(_, [], [], _, _, [], [], [], [], []) :- !, fail.

:- mode extract_CnL_from_pos_list(+, -, ?).
extract_CnL_from_pos_list([], CnL, CnL) :- !.
extract_CnL_from_pos_list([(X,Y)|PosL], [X|CnL0], CnL1) :-
    extract_CnL_from_pos_list(PosL, CnL0, CnL1).

:- mode exists_common_or_revolt_pattern(+, -, -, +).
exists_common_or_revolt_pattern(BltKey, ComPosL, RevPosL, TbyG0) :-
    refer_guard_table(TbyG0, BltKey, ComPosL0), 
    sort(ComPosL0, ComPosL1), sort_1(ComPosL1, ComPosL),
    get_revolt_pos_list(ComPosL, BltKey, RevPosL, TbyG0).    

:- mode get_revolt_pos_list(+, +, -, +).    
get_revolt_pos_list([(X,Y)], BltKey, RevPosL, TbyG0) :- !,     % common is 1 
    get_revolt_pattern_of(BltKey, RevPosKey), RevPosKey \== [],
    find_revolt_list(RevPosKey, RevPosL, [], TbyG0).
get_revolt_pos_list(ComPosL, BltKey, RevPosL, TbyG0) :-
    get_revolt_pattern_of(BltKey, RevPosKey),
    find_revolt_list(RevPosKey, RevPosL, [], TbyG0).

:- mode get_revolt_pattern_of(+, -).
get_revolt_pattern_of(less_than(X,Y), [not_less_than(X,Y)]) :- !.
get_revolt_pattern_of(not_less_than(X,Y), [less_than(X,Y)]) :- !.
get_revolt_pattern_of(equal(X,Y), [not_equal(X,Y)]) :- !.
get_revolt_pattern_of(not_equal(X,Y), [equal(X,Y)]) :- !.
get_revolt_pattern_of(_,     []) :- !.

:- mode find_revolt_list(+, -, ?, +).
find_revolt_list([], RevoltL, RevoltL, _) :- !.
find_revolt_list([One|RevoltKey], [Revolt|RevoltL0], RevoltL1, TbyG0) :-
    exists_revolt_pattern(One, TbyG0, Revolt), !,
    find_revolt_list(RevoltKey, RevoltL0, RevoltL1, TbyG0).
find_revolt_list([_|RevoltKey], RevoltL0, RevoltL1, TbyG0) :-
    find_revolt_list(RevoltKey, RevoltL0, RevoltL1, TbyG0).

:- mode exists_revolt_pattern(+, +, -).
exists_revolt_pattern((One,Other), TbyI0, Revolt) :- !,
    exists_revolt_pattern(One, TbyI0, ROne),
    exists_revolt_pattern(Other, TbyI0, ROther),
    is_column_equal(ROne, ROther, Revolt), Revolt \== [].
exists_revolt_pattern(One, TbyI0, Revolt) :- !,
    refer_guard_table(TbyI0, One, [Revolt]).

:- mode is_column_equal(+, +, -).
is_column_equal((X,Y), (X,Z), ((X,Y),(X,Z))) :- !.
is_column_equal(_, _, []) :- !.

:- mode divide_clause_list_with(+, +, +, +, +).
divide_clause_list_with([], _, _, UnmatchedL, UnmatchedL) :- !.
divide_clause_list_with([One|CnL], ComPosL, RevPosL, Un0, Un1) :-
    exists_in_common_or_revolt(One, ComPosL, NewComPos, RevPosL, NewRevPos), !,
    divide_clause_list_with(CnL, NewComPos, NewRevPos, Un0, Un1).
divide_clause_list_with([One|CnL], ComPosL, RevPosL, [One|Un0], Un1) :-
    divide_clause_list_with(CnL, ComPosL, RevPosL, Un0, Un1).

:- mode exists_in_common_or_revolt(+, +, -, +, -).
exists_in_common_or_revolt(One, Common, NewCommon, Revolt, Revolt) :-
    exists_element_in_list(Common, One, NewCommon), !.
exists_in_common_or_revolt(One, Common, Common, Revolt, NewRevolt) :-
    exists_element_in_list(Revolt, One, NewRevolt), !.

:- mode exists_element_in_list(+, +, -).
exists_element_in_list([(X,Y)|Common], X, Common) :- !.
exists_element_in_list([(X,Y)|Common], Key, NewCommon) :- X < Key, !, 
    exists_element_in_list(Common, Key, NewCommon).

:- mode lift_up_builtin_args(+, -, +, +, -). 
lift_up_builtin_args(Blt, BltList, REG, TbyV0-TbyV1, RegVarPair) :-
    builtin(Blt, _, _, PredList, _, _, _),
    attach_predlist(PredList, NormList, [Blt]),
    gen_indexed_blt_code(NormList, REG, TbyV0-TbyV1, 
                                        RegVarPair-[],
					BltList-[]).

:- mode attach_predlist(+, -, ?).
attach_predlist([], Norm, Norm) :- !.
attach_predlist([One|PredList], [One|Norm0], Norm1) :-
    attach_predlist(PredList, Norm0, Norm1).

:- mode gen_indexed_blt_code(+, +, +, +, +).
gen_indexed_blt_code([], Reg-Reg, TbyV-TbyV, 
                                  RegVar-RegVar, 
				  BltList-BltList) :- !.
gen_indexed_blt_code([Blt|NormList], REG, TbyV0-TbyV1, REGVAR, 
                     BltList0-BltList2) :- 
    builtin(Blt, _, _, _, _, check, _), !,
    arg(1, Blt, Arg),
    check_if_pred_already_set(Arg, Blt, TbyV0, BltList0, BltList1),
    gen_indexed_blt_code(NormList, REG, TbyV0-TbyV1, REGVAR, 
                         BltList1-BltList2). 
gen_indexed_blt_code([Blt|NormList], Reg0-Reg2, 
                                     TbyV0-TbyV3, 
                                     RegVar0-RegVar2,
                                     BltList0-BltList2) :- 
    builtin(Blt, Input, Output, _, TypeList, _, _),
    functor(Blt, F, A), functor(NewBlt, F, A),
    expand_input_args(Input, Blt, NewBlt, Reg0, TbyV0,
                                          BltList0-[NewBlt|BltList1]),
    expand_output_args(Output, Blt, NewBlt, Reg0-Reg1, 
                                            TbyV0-TbyV1,
					    RegVar0-RegVar1),
    set_var_type_of_indexed_blt(TypeList, TbyV1, TbyV2),
%%%    is_indexed_blt_vector_element(NewBlt, TbyV2, TbyV3),
    gen_indexed_blt_code(NormList, Reg1-Reg2, TbyV2-TbyV3, 
                                   RegVar1-RegVar2,
                                   BltList1-BltList2).

:- mode check_if_pred_already_set(+, +, +, -, ?).
check_if_pred_already_set(Arg, Blt, _, BltList, BltList) :-
    atomic(Arg), !.
check_if_pred_already_set(Arg0, Blt, TbyV, BltList0, BltList1) :-
    kl1_var_or_derefed(Arg0, Arg),                         %%%%%
    refer_guard_table(TbyV, Arg, Reg),
  ( refer_guard_table(TbyV, '$TYPE'(Reg), Type),
	check_both_arg_type(Blt, Type), !, BltList0 = BltList1 ;
    functor(Blt, F, A), functor(NewBlt, F, A),
    arg(1, NewBlt, Reg), BltList0 = [NewBlt|BltList1] ).

:- mode check_both_arg_type(+, +).
check_both_arg_type(wait(_), _) :- !.
check_both_arg_type(Blt,     Type) :- 
    functor(Blt, F, _), F == Type.

:- mode expand_input_args(+, +, +, +, +, +).
expand_input_args([], _, _, _, _, Blt-Blt) :- !.
expand_input_args([One|Input], Blt, NewBlt, Reg, TbyV, BLTLIST) :- 
    arg(One, Blt, E0), kl1_var_or_derefed(E0, E),            %%%%%
    search_variable_position_in_head(E, TbyV, RegPos), !,
    arg(One, NewBlt, RegPos),
    expand_input_args(Input, Blt, NewBlt, Reg, TbyV, BLTLIST).
expand_input_args([One|Input], Blt, NewBlt, Reg0, TbyV,
                                    [put_constant(E,Reg0)|BltL0]-BltL1) :- 
    arg(One, Blt, E), atomic(E), !, 
    arg(One, NewBlt, Reg0),
    Reg1 is Reg0+1,
    expand_input_args(Input, Blt, NewBlt, Reg1, TbyV, BltL0-BltL1).
expand_input_args([One|Input], Blt, NewBlt, Reg, TbyV, BLTLIST) :-
    arg(One, Blt, E),
    arg(One, NewBlt, E),
    error('Illegal argument in guard builtin : ~w in ~w', [E, Blt]),
    expand_input_args(Input, Blt, NewBlt, Reg, TbyV, BLTLIST).

:- mode expand_output_args(+, +, +, +, +, +).
expand_output_args([], _, _, Reg-Reg, TbyV-TbyV, RegVar-RegVar) :- !.
expand_output_args([Index|Output], Blt, NewBlt, Reg0-Reg2, TbyV0-TbyV2,
                                                RegVar0-RegVar2) :-
    arg(Index, Blt, E0), kl1_var_or_derefed(E0, E), !,         %%%%%
    expand_one_output_arg(E, Reg, Reg0-Reg1, TbyV0-TbyV1, RegVar0-RegVar1),
    arg(Index, NewBlt, Reg),
    expand_output_args(Output, Blt, NewBlt, Reg1-Reg2, TbyV1-TbyV2,
                                            RegVar1-RegVar2).
expand_output_args([Index|Output], Blt, NewBlt, Reg0-Reg2, TBYV, 
                                   [(Reg0,'$ATOMIC'(E))|RegVar0]-RegVar1) :-
    arg(Index, Blt, E), atomic(E), !, 
    arg(Index, NewBlt, Reg0),
    Reg1 is Reg0 + 1,
    expand_output_args(Output, Blt, NewBlt, Reg1-Reg2, TBYV, RegVar0-RegVar1).
expand_output_args([Index|Output], Blt, NewBlt, REG, TBYV, REGVAR) :-
    arg(Index, Blt, E),
    arg(Index, NewBlt, E),
    error('Illegal argument in guard builtin : ~w in ~w', [E, Blt]),
    expand_output_args(Output, Blt, NewBlt, REG, TBYV, REGVAR).

:- mode expand_one_output_arg(+, -, +, +, +).
expand_one_output_arg(E, Reg_Pos, Reg-Reg, TbyV-TbyV, RegVar-RegVar) :-
    search_variable_position_in_head(E, TbyV, Reg_Pos),    
    integer(Reg_Pos), !.
expand_one_output_arg(E, Reg0, Reg0-Reg1, TbyV0-TbyV1, 
                                          [(Reg0,E)|RegVar]-RegVar) :-
    Reg1 is Reg0+1,
    update_guard_table(TbyV0, E, Reg0, TbyV1).

:- mode search_variable_position_in_head(+, +, -).
search_variable_position_in_head(E, TbyV, Reg_Pos) :-
    refer_guard_table(TbyV, E, Reg_Pos), !.

:- mode set_var_type_of_indexed_blt(+, +, -).
set_var_type_of_indexed_blt([(V0,Type)|TypeList], TbyV0, TbyV2) :-
    kl1_var_or_derefed(V0, V), !,                        %%%%%
    refer_guard_table(TbyV0, V, R),
    update_guard_table(TbyV0, '$TYPE'(R), Type, TbyV1),
    set_var_type_of_indexed_blt(TypeList, TbyV1, TbyV2).
set_var_type_of_indexed_blt([_|TypeList], TbyV0, TbyV1) :- !,
    set_var_type_of_indexed_blt(TypeList, TbyV0, TbyV1).
set_var_type_of_indexed_blt([], TbyV, TbyV) :- !.

:- mode is_indexed_blt_vector_element(+, +, -).
is_indexed_blt_vector_element(vector_element(V,I,E), TbyV0, TbyV1) :- !,
    refer_guard_table(TbyV0, E, R),
    update_guard_table(TbyV0, '$ATTRIBUTE'(R), element(V, I), TbyV1).
is_indexed_blt_vector_element(_, TbyV, TbyV) :- !.

:- mode modify_common_clauses(+, +, +, +).
modify_common_clauses([], _, TbyI-TbyI, CommonT-CommonT) :- !.
modify_common_clauses([(X,Y)|CommonL], RegVarPair, TbyI0-TbyI2, 
                                                   CommonT0-CommonT2) :-
    get_tree(CommonT0, X, Clause0),
    get_clause_variable_no(Clause0, Nv0),
    refer_guard_table(TbyI0, (X,Y), Blt),
    set_indexed_args_to_head(RegVarPair, Blt, Nv0-Nv, Clause0-Clause1, 
					              true-NewGuard),
    update_guard_table(TbyI0, (X,Y), NewGuard, TbyI1),
    update_clause_variable_no(Clause1, Nv, NewClause),
    update_guard_table(CommonT0, X, NewClause, CommonT1),
    modify_common_clauses(CommonL, RegVarPair, TbyI1-TbyI2, 
                                               CommonT1-CommonT2).

:- mode modify_revolt_clauses(+, +).
modify_revolt_clauses([], TbyI-TbyI) :- !.
modify_revolt_clauses([One|RevoltL], TbyI0-TbyI2) :-
    flatten_position(One, NewOne, []),
    set_true_at_TbyI(NewOne, TbyI0, TbyI1),
    modify_revolt_clauses(RevoltL, TbyI1-TbyI2).

:- mode flatten_position(+, -, ?).
flatten_position((X,Y), [(X,Y)|Next], Next) :- 
    integer(X), integer(Y), !.
flatten_position((X,Y), NewOne0, NewOne2) :- 
    flatten_position(X, NewOne0, NewOne1),
    flatten_position(Y, NewOne1, NewOne2).

:- mode set_true_at_TbyI(+, +, -).
set_true_at_TbyI([], TbyI, TbyI) :- !.
set_true_at_TbyI([One|Cdr], TbyI0, TbyI2) :-
    update_guard_table(TbyI0, One, true, TbyI1),
    set_true_at_TbyI(Cdr, TbyI1, TbyI2).

:- mode classify_guard_goal(+, +, +, -, -, -, +).
classify_guard_goal(ComCnL,  RevCnL,  UnmatchedL,
                    CommonT, RevoltT, UnmatchedT,
                    TbyC) :-
    intern_clauses_by_clause_list(ComCnL, TbyC, [], CommonT0),
    update_tree(CommonT0, '$CLAUSE_NO_LIST', ComCnL, CommonT),
    intern_clauses_by_clause_list(RevCnL, TbyC, [], RevoltT0),
    update_tree(RevoltT0, '$CLAUSE_NO_LIST', RevCnL, RevoltT),
    intern_clauses_by_clause_list(UnmatchedL, TbyC, [], UnmatchedT0),
    update_tree(UnmatchedT0, '$CLAUSE_NO_LIST', UnmatchedL, UnmatchedT).

:- mode intern_clauses_by_clause_list(+, +, +, -).
intern_clauses_by_clause_list([], _, Tree, Tree) :- !.
intern_clauses_by_clause_list([Cn|MList], TbyC, Tree0, Tree2) :- 
    get_tree(TbyC, Cn, One),
    update_guard_table(Tree0, Cn, One, Tree1),
    intern_clauses_by_clause_list(MList, TbyC, Tree1, Tree2).

:- mode get_input_output_arg(+, -, -).
get_input_output_arg(Blt, Input, Output) :- 
    builtin(Blt, Input, Output, _, _, _, _).

:- mode set_indexed_args_to_head(+, +, +, +, +).
set_indexed_args_to_head([], _, Nv-Nv, Clause-Clause, Guard-Guard) :- !.
set_indexed_args_to_head([(Reg,N)|RegVarPair], Blt, Nv0-Nv2, 
	                                            Clause0-Clause3,
					            Guard0-Guard1) :-
    tell_kl1var_or_atomic(N, Res),
    create_kl1_var(NewVar, Nv0, Nv1),
    get_predefined_head(Clause0, Head0),
    update_predefined_head_arg(Head0, Reg, NewVar, Head1),
    update_predefined_head(Clause0, Head1, Clause1),
    update_used_reg_no(Clause1, Reg, Clause2),
    set_indexed_args_to_head(RegVarPair, Blt, Nv1-Nv2, 
					      Clause2-Clause3,
					      (NewVar=Res,Guard0)-Guard1).

:- mode tell_kl1var_or_atomic(+, -).
tell_kl1var_or_atomic('$ATOMIC'(C), C) :- !.
tell_kl1var_or_atomic(V,            V) :- kl1_var(V), !.
tell_kl1var_or_atomic(V,            error(tell_kl1var_or_atomic)) :-
    error('Illegal data type in tell_kl1var_or_atomic: ~w', [V]).

:- mode update_predefined_reg_list(+, +, -).
update_predefined_reg_list([], TbyV, TbyV) :- !.
update_predefined_reg_list([(Reg,N)|RegVarPair], TbyV0, TbyV2) :-
    integer(N), !,
    update_guard_table(TbyV0, '$VAR'(N), Reg, TbyV1),
    update_predefined_reg_list(RegVarPair, TbyV1, TbyV2).
update_predefined_reg_list([_|RegVarPair], TbyV0, TbyV1) :-
    update_predefined_reg_list(RegVarPair, TbyV0, TbyV1).

:- mode refer_guard_table(+, +, ?).
refer_guard_table(Table, Key, Value) :- get_tree(Table, Key, Value).

:- mode update_guard_table(+, +, ?, -).
update_guard_table(Table0, Key, Value, Table1) :- 
    update_tree(Table0, Key, Value, Table1).

:- mode intern_guard_table(+, +, ?, -).
intern_guard_table(Table0, Key, Value, Table1) :- 
    intern(Table0, Key, Value, Table1).

:- mode create_clause_table(-).
create_clause_table(Clause) :- 
    array(7, Clause0, []), aset(Clause0, 0, '$CLAUSE', Clause).

:- mode initiate_clause_table(+, +, +, +, +, -).
initiate_clause_table(Clause, Head, Depend, Cn, Nv, Array) :- 
    array(7, Array0),
    aset(Array0, 0, '$CLAUSE', Array1),
    aset(Array1, 1, Cn,        Array2),
    aset(Array2, 2, Nv,        Array3),
    aset(Array3, 3, Used_Reg,  Array4),
    aset(Array4, 4, Depend,    Array5),
    aset(Array5, 5, Head,      Array6),
    aset(Array6, 6, Clause,    Array).

:- mode is_clause(+).
is_clause(Clause) :- aref(Clause, 0, '$CLAUSE').

:- mode get_clause_no(+, -).
get_clause_no(Clause, Cn) :- aref(Clause, 1, Cn).

:- mode get_clause_variable_no(+, -).
get_clause_variable_no(Clause, Nv) :- aref(Clause, 2, Nv).

:- mode get_used_reg_no(+, -).
get_used_reg_no(Clause, Reg) :- aref(Clause, 3, Reg).

:- mode get_clause_dependency(+, -).
get_clause_dependency(Clause, Depend) :- aref(Clause, 4, Depend).

:- mode get_predefined_head(+, -).
get_predefined_head(Clause, Head) :- aref(Clause, 5, Head).

:- mode get_original_clause(+, -).
get_original_clause(Clause, Cls) :- aref(Clause, 6, Cls).

:- mode update_clause_no(+, +, -).
update_clause_no(Clause0, Cn, Clause1) :- 
    aset(Clause0, 1, Cn, Clause1).

:- mode update_clause_variable_no(+, +, -).
update_clause_variable_no(Clause0, Nv, Clause1) :- 
    aset(Clause0, 2, Nv, Clause1).

:- mode update_used_reg_no(+, +, -).
update_used_reg_no(Clause0, Reg, Clause1) :- 
    aset(Clause0, 3, Reg, Clause1).

:- mode update_clause_dependency(+, +, -).
update_clause_dependency(Clause0, Depend, Clause1) :- 
    aset(Clause0, 4, Depend, Clause1).

:- mode update_predefined_head(+, +, -).
update_predefined_head(Clause0, Head, Clause1) :- 
    aset(Clause0, 5, Head, Clause1).

:- mode update_original_clause(+, +, -).
update_original_clause(Clause0, Cls, Clause1) :- 
   aset(Clause0, 6, Cls, Clause1).

:- mode update_predefined_head_arg(+, +, ?, -).
update_predefined_head_arg(Head0, Pos, Data, Head1) :- 
    aset(Head0, Pos, Data, Head1).


%%%%% Reconstrcuting an indexed clause 

:- mode reconstruct_clauses(+, +, -, ?).
reconstruct_clauses([One|Clses], Used_Reg, [New|Conv0], Conv1) :- !,
    reconstruct_one_clause(One, Used_Reg, New), 
    reconstruct_clauses(Clses, Used_Reg, Conv0, Conv1).
reconstruct_clauses([], Used_Reg, Conv, Conv) :- !.

:- mode reconstruct_one_clause(+, +, -).
reconstruct_one_clause(ClsTbl0, Used_Reg, ClsTbl1) :-
    reconstruct_indexed_head(ClsTbl0, Used_Reg, H),
    get_original_clause(ClsTbl0, Cls),
    take_apart_clause(Cls, _, G, B),
    update_original_clause(ClsTbl0, (H:-G|B), ClsTbl1).

:- mode reconstruct_indexed_head(+, +, -).
reconstruct_indexed_head(Cls, Used_Reg, Head) :-
    get_predefined_head(Cls, Head0),
    aref(Head0, 0, F), functor(Head, F, Used_Reg),
    make_new_head(Used_Reg, Head0, Head).

:- mode make_new_head(+, +, +).
make_new_head(0, _, _) :- !.
make_new_head(Reg, Head0, Head) :-
    aref(Head0, Reg, E0), 
    convert_one_predefined_head_arg(E0, E),
    arg(Reg, Head, E),
    Reg1 is Reg - 1,
    make_new_head(Reg1, Head0, Head).

:- mode convert_clause_tree_to_list(+, +, +, +, -, ?).
convert_clause_tree_to_list([], _, _, _, Clses, Clses) :- !.
convert_clause_tree_to_list([Cn|CList], TbyC, Reg, TABLE, [Cls|Clses0], 
                                                          Clses1) :-
    reconstruct_one_clause_with_guard(Cn, TbyC, Reg, TABLE, Cls),
    convert_clause_tree_to_list(CList, TbyC, Reg, TABLE, Clses0, Clses1).

:- mode reconstruct_one_clause_with_guard(+, +, +, +, -).
reconstruct_one_clause_with_guard(Cn, TbyC, Reg, TbyG-TbyI-TbyV, ClsTbl1) :-
    refer_guard_table(TbyC, Cn, ClsTbl0),
    reconstruct_indexed_head_with_guard(ClsTbl0, Reg, TbyV, H),
    reconstruct_indexed_guard(Cn, TbyI, G),
    get_original_clause(ClsTbl0, Cls),
    take_apart_clause(Cls, _, _, B),
    update_original_clause(ClsTbl0, (H:-G|B), ClsTbl1).

:- mode reconstruct_indexed_head_with_guard(+, +, +, -).
reconstruct_indexed_head_with_guard(Cls, Used_Reg, TbyV, Head) :-
    get_predefined_head(Cls, Head0),
    aref(Head0, 0, F), functor(Head, F, Used_Reg),
    make_new_head_with_guard(Used_Reg, Head0, TbyV, Head).

:- mode make_new_head_with_guard(+, +, +, +).
make_new_head_with_guard(0, _, _, _) :- !.
make_new_head_with_guard(Reg, Head0, TbyV, Head) :-
    aref(Head0, Reg, E0), 
    convert_one_predefined_head_arg(E0, E1),
  ( refer_guard_table(TbyV, '$TYPE'(Reg), Type), 
        Type \== [], Type \== var, !,        % Type \== var is attached 
                                             % 88.09.08 Y.Kimura
	attach_type_information(E1, '$TYPE'(Type), E) ;
    E = E1 ),
    arg(Reg, Head, E),
    Reg1 is Reg - 1,
    make_new_head_with_guard(Reg1, Head0, TbyV, Head).

:- mode attach_type_information(+, +, -).
attach_type_information(Type@E, Type, Type@E) :- !.
attach_type_information(Flag@E, Type, Flag@E) :- is_indexing_flag(Flag), !.
attach_type_information(E, Type, Type@E) :- kl1_var(E), !.

:- mode convert_one_predefined_head_arg(+, -).
convert_one_predefined_head_arg(Type@E0, Type@E) :-
    is_indexing_flag(Type), !, 
    convert_one_predefined_head_arg(E0, E).
convert_one_predefined_head_arg(E0, E0) :- kl1_var(E0), !.
convert_one_predefined_head_arg(E0, E) :- functor(E0, '$array', A), !, 
    convert_array_to_list(A, E0, [], List),
    E =.. List.
convert_one_predefined_head_arg(E, E) :- !.

:- mode convert_array_to_list(+, +, +, -).
convert_array_to_list(0, Array, L, L) :- !.
convert_array_to_list(A, Array, L0, L) :- 
    A1 is A - 1,
    aref(Array, A1, E0), 
    convert_one_predefined_head_arg(E0, E),
    convert_array_to_list(A1, Array, [E|L0], L).

:- mode reconstruct_indexed_guard(+, +, -).
reconstruct_indexed_guard(Cn, TbyI, Guard) :-
    refer_guard_table(TbyI, '$NUMBER_OF_GUARDS'(Cn), N),
    create_guard_goals_loop(N, Cn, TbyI, true, Guard).

:- mode create_guard_goals_loop(+, +, +, +, -).
create_guard_goals_loop(0, _, _, Guard, Guard) :- !.
create_guard_goals_loop(N, Cn, TbyI, Guard0, Guard) :-
    N1 is N-1,
    refer_guard_table(TbyI, (Cn, N), G),
  ( G == true, !, create_guard_goals_loop(N1, Cn, TbyI, Guard0, Guard) ;
    create_guard_goals_loop(N1, Cn, TbyI, (G,Guard0), Guard) ).


%%%% COMPILATION OF THE INDEXED TREE

:- mode compile_indexed_tree(+, +, ?, -, ?).
compile_indexed_tree(nonvar(Expand, Nonvar, Var), 
                     PredGc, Fail, Code0, Code4) :- !,
    get_indexing_reg(Expand, In, Code0, Code1),
    compile_nonvar_tree(Nonvar, PredGc, Next, Code1, Code2),
    generate_fail_label(Nonvar, Var, Next, Fail, Code2, Code3),
    compile_indexed_tree(Var, PredGc, Fail, Code3, Code4).
compile_indexed_tree(guard(BltList, Matched, Unmatched), 
	             PredGc, Fail, Code0, Code3) :- !,
    compile_matched_tree(BltList, Matched, PredGc, Next, Code0, Code1),
    generate_fail_label(Matched, Unmatched, Next, Fail, Code1, Code2),
    compile_indexed_tree(Unmatched, PredGc, Fail, Code2, Code3).
compile_indexed_tree(leaf(Cls), (Pred,Gc), Fail, Code0, Code1) :- !,
    compile_leaf_clause(Gc, Cls, Fail, Code0, Code1).
compile_indexed_tree(Clses, PredGc, Fail, Code0, Code1) :- !,
    compile_try_clauses(Clses, PredGc, Fail, Code0, Code1).

:- mode get_indexing_reg(+, -, -, ?).
get_indexing_reg(car(In,Reg), Reg, [read_car(In,Reg)|Code], Code) :- !.
get_indexing_reg(cdr(In,Reg), Reg, [read_cdr(In,Reg)|Code], Code) :- !.
get_indexing_reg(element(In,Index,Reg), Reg, 
	         [read_element(In,Index,Reg)|Code], Code) :- !.
get_indexing_reg(In, In, Code, Code) :- integer(In), !.
get_indexing_reg(In, In, Code, Code) :- 
    error('Invalid indexing key: ~w', [In]).

:- mode compile_nonvar_tree(+, +, ?, -, ?).
compile_nonvar_tree([], _, _, Code, Code) :- !.
compile_nonvar_tree(wait(In, Type, Wait), PredGc, Fail, 
		    [try_me_else(Fail),wait(In, Fail)|Code0], Code3) :- 
    compile_typed_tree(Type, PredGc, Next, Code0, Code1),
    generate_fail_label(Type, Wait, Next, Fail, Code1, Code2),    
    compile_indexed_tree(Wait, PredGc, Fail, Code2, Code3).

:- mode compile_typed_tree(+, +, ?, -, ?).
compile_typed_tree([], _, _, Code, Code) :- !.
compile_typed_tree(type(In, Att, Itt, Ltt, Vtt, Stt, Ett), PredGc, Fail, 
		   Code0, Code1) :-
    generate_type_and_tree_list([Ltt,Att,Itt,Vtt,Stt,Ett], 
                                Type_List-[], 0-Length),
    Length > 0, 3 > Length, !,
    compile_type_and_tree_pair(Type_List, PredGc, Next, Fail, Code0, Code1).
compile_typed_tree(type(In, Att, Itt, Ltt, Vtt, Stt, Ett), PredGc, Fail, 
		   [switch_on_type(In,Al,Il,Ll,Vl,Sl,El)|Code0], 
		   Code6) :-
    compile_list_tree(Ltt, PredGc, Fail, Ll, Code0, Code1),
    compile_atom_tree(Att, PredGc, Fail, Al, Code1, Code2),
    compile_integer_tree(Itt, PredGc, Fail, Il, Code2, Code3),
    compile_vector_tree(Vtt, PredGc, Fail, Vl, Code3, Code4),
    compile_string_tree(Stt, PredGc, Fail, Sl, Code4, Code5),
    compile_else_tree(Ett, PredGc, Fail, El, Code5, Code6).

:- mode generate_fail_label(+, +, ?, ?, -, ?).
generate_fail_label([], _, _, _, Code, Code) :- !.
generate_fail_label(_, [], Fail, Fail, Code, Code) :- !.
generate_fail_label(_, _,  Next, _, [label(Next)|Code], Code) :- !.

:- mode generate_type_and_tree_list(+, +, +).
generate_type_and_tree_list([], Type_List-Type_List, Length-Length) :- !.
generate_type_and_tree_list([Tree|Cdr], 
                            [(Type,Tree)|List0]-List1, L0-Length) :-
    Tree \== [], !,
    L1 is L0+1,
    functor(Tree, Type, _), 
    generate_type_and_tree_list(Cdr, List0-List1, L1-Length).
generate_type_and_tree_list([_|Cdr], LIST, LENGTH) :-
    generate_type_and_tree_list(Cdr, LIST, LENGTH).

:- mode compile_type_and_tree_pair(+, +, ?, ?, -, ?).
compile_type_and_tree_pair([(Type,Tree)], PredGc, Next, Fail, 
                           [label(Next)|Code0], Code1) :- !,
    compile_tree_by_type(Type, Tree, PredGc, Fail, Fail, Code0, Code1).
compile_type_and_tree_pair([(Type,Tree)|Cdr], PredGc, Next, Fail, 
                           [label(Next)|Code0], Code2) :-
    compile_tree_by_type(Type, Tree, PredGc, Next1, Fail, Code0, Code1),
    compile_type_and_tree_pair(Cdr, PredGc, Next1, Fail, Code1, Code2).

:- mode compile_tree_by_type(+, +, +, ?, ?, -, ?).
compile_tree_by_type(atom, atom(In,Const,Type), PredGc, Next, Fail, 
                     [is_atom(In,Next)|Code0], 
%%%%% for MERGE      [try_me_else(Next),is_atom(In,Next)|Code0], 
		     Code3) :- !,
    compile_constant_tree(Const, In, PredGc, AtomType, Code0, Code1),
    generate_fail_label(Const, Type, AtomType, Fail, Code1, Code2),
    compile_type_tree(Type, In, PredGc, Fail, Code2, Code3).
compile_tree_by_type(integer, integer(In,Const,Type), PredGc, Next, Fail, 
                     [is_integer(In,Next)|Code0], 
%%%%% for MERGE      [try_me_else(Next),is_integer(In,Next)|Code0], 
		     Code3) :- !,
    compile_constant_tree(Const, In, PredGc, IntType, Code0, Code1),
    generate_fail_label(Const, Type, IntType, Fail, Code1, Code2),
    compile_type_tree(Type, In, PredGc, Fail, Code2, Code3).
compile_tree_by_type(float, float(In,FloatL,Ftype), PredGc, Next, Fail, 
                     [is_float(In,Next)|Code0], 	% 890404 Nishizaki
%%%%% for MERGE      [try_me_else(Next),is_float(In,Next)|Code0], 
		     Code3) :- !,
    compile_float_clauses(FloatL, In, PredGc, FloatType, Code0, Code1),
    generate_fail_label(FloatL, Ftype, FloatType, Fail, Code1, Code2),
    compile_type_tree(Ftype, In, PredGc, Fail, Code2, Code3).
compile_tree_by_type(list, list(In,Cons), PredGc, Next, Fail, 
                     [is_list(In,Next)|Code0], 
%%%%% for MERGE      [try_me_else(Next),is_list(In,Next)|Code0], 
                     Code1) :- !,
    compile_cons_tree(Cons, PredGc, Fail, Code0, Code1).
compile_tree_by_type(vector, vector(In,Vect,Vtype), PredGc, Next, Fail, 
                     [is_vector(In,Next)|Code0], 
%%%%% for MERGE      [try_me_else(Next),is_vector(In,Next)|Code0], 
                     Code3) :- !,
    compile_arity_tree(Vect, In, PredGc, VectType, Code0, Code1),
    generate_fail_label(Vect, Vtype, VectType, Fail, Code1, Code2),
    compile_type_tree(Vtype, In, PredGc, Fail, Code2, Code3).
compile_tree_by_type(string, string(In,StrgL,Stype), PredGc, Next, Fail, 
                     [is_string(In,Next)|Code0], 
%%%%% for MERGE      [try_me_else(Next),is_string(In,Next)|Code0], 
		     Code3) :- !,
    compile_string_clauses(StrgL, PredGc, StrgType, Code0, Code1),
    generate_fail_label(StrgL, Stype, StrgType, Fail, Code1, Code2),
    compile_indexed_tree(Stype, PredGc, Fail, Code2, Code3).
compile_tree_by_type(else, else(In,ElseL), PredGc, Next, Fail, 
                     Code0, Code1) :- !,
    compile_else_clauses(ElseL, PredGc, Fail, Code0, Code1).


%%%%% Atoms or Integers

:- mode compile_atom_tree(+, +, ?, ?, -, ?).
compile_atom_tree([], _, Fail, Fail, Code, Code) :- !.
compile_atom_tree(atom(In, Const, Type), PredGc, Fail, Alab,
		    [label(Alab)|Code0], Code3) :- !, 
    compile_constant_tree(Const, In, PredGc, Next, Code0, Code1),
    generate_fail_label(Const, Type, Next, Fail, Code1, Code2),
    compile_type_tree(Type, In, PredGc, Fail, Code2, Code3).

:- mode compile_integer_tree(+, +, ?, ?, -, ?).
compile_integer_tree([], _, Fail, Fail, Code, Code) :- !.
compile_integer_tree(integer(In, Const, Type), PredGc, Fail, Alab,
		    [label(Alab)|Code0], Code3) :- !, 
    compile_constant_tree(Const, In, PredGc, Next, Code0, Code1),
    generate_fail_label(Const, Type, Next, Fail, Code1, Code2),
    compile_type_tree(Type, In, PredGc, Fail, Code2, Code3).

:- mode compile_constant_tree(+, +, +, ?, -, ?).
compile_constant_tree([], _, _, _, Code, Code) :- !.
compile_constant_tree([(Key,Clses)], In, PredGc, Fail, 
                      [try_me_else(Fail),
		       test_constant(Const,In,Fail)|Code0], Code1) :- !,
    arg(1, Key, Const),
    compile_indexed_tree(Clses, PredGc, Fail, Code0, Code1).
compile_constant_tree(CnstList, In, PredGc, Fail,
		      [try_me_else(Fail),
		       branch_on_constant(In,BranchPair)|Code0], 
		      Code1) :-
    compile_branch_on_constant(CnstList, Fail, PredGc,
	                       BranchPair-[Fail], Code0, Code1).

:- mode compile_branch_on_constant(+, ?, +, +, -, ?).
compile_branch_on_constant([], _, _, BP-BP, Code, Code) :- !.
compile_branch_on_constant([(Key,One)|CnstList], Fail, PredGc,
	                   [(Const,Clab)|BP0]-BP1, 
			   [label(Clab)|Code0], Code2) :- 
    arg(1, Key, Const),
    compile_indexed_tree(One, PredGc, Fail, Code0, Code1),
    compile_branch_on_constant(CnstList, Fail, PredGc,
	                                       BP0-BP1, Code1, Code2).

:- mode compile_type_tree(+, +, +, ?, -, ?).
compile_type_tree([], _, _, _, Code, Code) :- !.
compile_type_tree([(Key,Clses)], In, PredGc, Fail, Code0, Code1) :- 
    compile_indexed_tree(Clses, PredGc, Fail, Code0, Code1).

%%%%% Floats	% 890404 Nishizaki

:- mode compile_float_tree(+, +, ?, ?, -, ?).
compile_float_tree([], _, Fail, Fail, Code, Code) :- !.
compile_float_tree(float(In, FloatL, Ftype), PredGc, Fail, Flab,
		    		     [label(Flab),
				      is_float(In,Fail)|Code0], Code3) :- !, 
    compile_float_clauses(FloatL, In, PredGc, Next, Code0, Code1),
    generate_fail_label(FloatL, Ftype, Next, Fail, Code1, Code2),
    compile_type_tree(Ftype, In, PredGc, Fail, Code2, Code3).

:- mode compile_float_clauses(+, +, +, ?, -, ?).
compile_float_clauses([], _, _, _, Code, Code) :- !.
compile_float_clauses([(Key,FClses)], In, PredGc, Fail,
		      [try_me_else(Fail),
		       test_constant(Const,In,Fail)|Code0], Code2) :-
    arg(1, Key, Const),
    compile_indexed_tree(FClses, PredGc, Fail, Code0, Code2).
compile_float_clauses([(Key,FClses)|Clses], In, PredGc, Fail,
		      [try_me_else(Next),
		       test_constant(Const,In,Next)|Code0], Code2) :-
    arg(1, Key, Const),
    compile_indexed_tree(FClses, PredGc, Next, Code0, [label(Next)|Code1]),
    compile_float_clauses(Clses, In, PredGc, Fail, Code1, Code2).

%%%%% Lists

:- mode compile_list_tree(+, +, ?, ?, -, ?).
compile_list_tree([], _, Fail, Fail, Code, Code) :- !.
compile_list_tree(list(In, Cons), PredGc, Fail, Llab, 
		  [label(Llab)|Code0], Code1) :-
    compile_cons_tree(Cons, PredGc, Fail, Code0, Code1).

:- mode compile_cons_tree(+, ?, ?, -, ?).
compile_cons_tree([], _, Fail, Code, Code) :- !.
compile_cons_tree(cons(Cons, Type), PredGc, Fail, Code0, Code3) :-
    compile_indexed_tree(Cons, PredGc, Next, Code0, Code1),
    generate_fail_label(Cons, Type, Next, Fail, Code1, Code2),
    compile_indexed_tree(Type, PredGc, Fail, Code2, Code3).

%%%%% Vectors

:- mode compile_vector_tree(+, +, ?, ?, -, ?).
compile_vector_tree([], _, Fail, Fail, Code, Code) :- !.
compile_vector_tree(vector(In, Vect, Type), 
	            PredGc, Fail, Vlab,
		    [label(Vlab)|Code0], Code3) :- !,
    compile_arity_tree(Vect, In, PredGc, Next, Code0, Code1),
    generate_fail_label(Vect, Type, Next, Fail, Code1, Code2),
    compile_type_tree(Type, In, PredGc, Fail, Code2, Code3).
    
:- mode compile_arity_tree(+, +, +, ?, -, ?).
compile_arity_tree([], _, _, _, Code, Code) :- !.
compile_arity_tree([(Key,Clses)], In, PredGc, Fail, 
                   [try_me_else(Fail),
		    test_arity(Key,In,Fail)|Code0], Code1) :-
    compile_indexed_tree(Clses, PredGc, Fail, Code0, Code1).
compile_arity_tree(VectList, In, PredGc, Fail,
	           [try_me_else(Fail),
		    branch_on_arity(In,BranchPair)|Code0], Code1) :-
    compile_branch_on_arity(VectList, PredGc, Fail,
	                    BranchPair-[Fail], Code0, Code1).

:- mode compile_branch_on_arity(+, +, ?, +, -, ?).
compile_branch_on_arity([], _, _, BP-BP, Code, Code) :- !.
compile_branch_on_arity([(Key,One)|VectList], PredGc, Fail,
	                [(Key,Alab)|BP0]-BP1, 
			[label(Alab)|Code0], Code2) :- 
    compile_indexed_tree(One, PredGc, Fail, Code0, Code1),
    compile_branch_on_arity(VectList, PredGc, Fail, 
	                                   BP0-BP1, Code1, Code2).

%%%%% Strings

:- mode compile_string_tree(+, +, ?, ?, -, ?).
compile_string_tree([], _, Fail, Fail, Code, Code) :- !.
compile_string_tree(string(In, StrgL, Stype), PredGc, Fail, Slab, 
                                      [label(Slab)|Code0], Code3) :- !,
    compile_string_clauses(StrgL, PredGc, Next, Code0, Code1),
    generate_fail_label(StrgL, Stype, Next, Fail, Code1, Code2),
    compile_indexed_tree(Stype, PredGc, Fail, Code2, Code3).

:- mode compile_string_clauses(+, +, ?, -, ?).
compile_string_clauses([], _, _, Code, Code) :- !.
compile_string_clauses([One|Clses], PredGc, Fail, Code0, Code2) :-
    compile_indexed_tree(One, PredGc, Fail, Code0, Code1),
    compile_string_clauses(Clses, PredGc, Fail, Code1, Code2).

%%%%% Other types

:- mode compile_else_tree(+, +, ?, ?, -, ?).
compile_else_tree([], _, Fail, Fail, Code, Code) :- !.
compile_else_tree(Const, PredGc, Fail, Flab, Code0, Code3) :-
    Const = float(In, Float, Type), !,		% 890404 Nishizaki
    compile_float_tree(Const, PredGc, Fail, Flab, Code0, Code3).
compile_else_tree(else(In, ElseL), PredGc, Fail, Elab, 
                                      [label(Elab)|Code0], Code1) :- !,
    compile_else_clauses(ElseL, PredGc, Next, Code0, Code1).

:- mode compile_else_clauses(+, +, ?, -, ?).
compile_else_clauses(ElseL, PredGc, Next, Code0, Code1) :-
    compile_string_clauses(ElseL, PredGc, Next, Code0, Code1).


%%%%% COMPILING THE GUARD PART INDEXING

:- mode compile_matched_tree(+, +, +, ?, -, ?).
compile_matched_tree(BltList, blt(Common, Revolt), 
                              PredGc, Fail, Code0, Code4) :-
    compile_indexed_guard(BltList, Next, Code0, Code1),
    compile_indexed_tree(Common, PredGc, Fail, Code1, Code2),    % 880722 Y.K.
    generate_fail_label(Common, Revolt, Next, Fail, Code2, Code3),
    compile_indexed_tree(Revolt, PredGc, Fail, Code3, Code4).

:- mode compile_indexed_guard(+, ?, -, ?).
compile_indexed_guard(BltList, Fail, [try_me_else(Fail)|Code0], Code1) :-
    compile_indexed_guard_list(BltList, Fail, Code0, Code1).

:- mode compile_indexed_guard_list(+, ?, -, ?).
compile_indexed_guard_list([], _, Code, Code) :- !.
compile_indexed_guard_list([Blt|BltList], Fail, Code0, Code2) :-
    builtin(Blt, _, _, _, _, Type, _), !,
    functor(Blt, F, A), 
  ( Type \== calculate, Type \== branch, !,  A1 is A+1,  % 890605 Nishizaki
	functor(NewBlt, F, A1),	arg(A1, NewBlt, Fail) ; 
    functor(NewBlt, F, A) ),
    NewBlt1 =.. [Type,NewBlt],
    compile_indexed_guard_args(A, Blt, NewBlt, Code0, [NewBlt1|Code1]),
    compile_indexed_guard_list(BltList, Fail, Code1, Code2).
compile_indexed_guard_list([Blt|BltList], Fail, [Blt|Code0], Code1) :-
    compile_indexed_guard_list(BltList, Fail, Code0, Code1).

:- mode compile_indexed_guard_args(+, +, +, -, ?).
compile_indexed_guard_args(0, _, _, Code, Code) :- !.
compile_indexed_guard_args(A, Blt, NewBlt, Code0, Code1) :-
    arg(A, Blt, E), integer(E), !, 
    arg(A, NewBlt, E), A1 is A - 1,
    compile_indexed_guard_args(A1, Blt, NewBlt, Code0, Code1).

:- mode compile_try_clauses(+, +, ?, -, ?). 
compile_try_clauses([], _, Fail, Code, Code) :- !.
compile_try_clauses([One], (Pred,Gc), Fail, Code0, Code1) :- !,
    compile_leaf_clause(Gc, One, Fail, Code0, Code1).
compile_try_clauses([One|Clses], (Pred,Gc), Fail, Code0, Code2) :-
    compile_leaf_clause(Gc, One, Next, Code0, [label(Next)|Code1]),
    compile_try_clauses(Clses, (Pred,Gc), Fail, Code1, Code2).


%%%%%% Sort_1/2 predicate 
%      NOTE: This predicate is temporarily introduced to remedy a bug of
%            sort/2 in SICStus Prolog.

:- mode sort_1(+, -).
sort_1([], []) :- !.
sort_1([X|Cdr0], [X|Cdr]) :- !, 
    drop_same_element_of_sort_1(Cdr0, X, Cdr1),
    sort_1(Cdr1, Cdr).

:- mode drop_same_element_of_sort_1(+, +, -).
drop_same_element_of_sort_1([], X, []) :- !.
drop_same_element_of_sort_1([X|Cdr0], X, Cdr) :- !,
    drop_same_element_of_sort_1(Cdr0, X, Cdr).
drop_same_element_of_sort_1(Cdr, X, Cdr) :- !.


%%%%%%%%%% Debugging tool

:- mode debug_display_tree(+).
debug_display_tree(Tree) :-
    seeing(OldFile), see(user),
    prompt(Old, '-> '), read(Index),
    debug_display_tree_1(Index, Tree, (Old,OldFile)).

:- mode debug_display_tree_1(+, +, +).
debug_display_tree_1(end, Tree, (Old,OldFile)) :- !, 
    prompt(_, Old), seen, see(OldFile).
debug_display_tree_1(Index, Tree, OLD) :- !,
    get_tree(Tree, Index, Value),
    display('Index = '), display(Index), 
    display('  '), display(Value), ttynl,
    read(NewIndex),
    debug_display_tree_1(NewIndex, Tree, OLD).



