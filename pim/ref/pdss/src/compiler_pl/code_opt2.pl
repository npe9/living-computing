%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%:- public is_branch_instruction/2, generate_branch_list/3.

%%%%% Code optimization routine 

:- mode optimize_kl1_code(+, +, +, +).
optimize_kl1_code(0, Code, _, L-L) :- output_code(0, Code).
optimize_kl1_code(1, Code, Pred, L0-L3) :-
%    write('%%%% Before code optimization'), nl,
%    output_code(0, Code), nl,
    L1 is L0+1,
%    write('%%%% Before give address of labels'), nl,
    give_address_of_labels(Code, Code1, [], Pred, L1-L2, []-Ltree), 
%    write('%%%% Before delete redundant labels'), nl,
    delete_redundant_labels(Code1, Code2, [], Ltree),
%    write('%%%%% After give_and_delete_label_instructions'), nl,
%    output_code(0, Code2), nl,
    merge_instructions([label(Pred/L0)|Code2], MrgdCode, []),
%    write('%%%%% After merge_instructions'), nl,
%    output_code(0, MrgdCode), nl,
    create_block_list(MrgdCode, 0-N, Pred, L2-L3, []-Called, []-Block0),
%    write('%%%%% After create_block_list'), nl,
%    print_block(0, N, Block0),
    gen_optimized_code(0, N, Block0-Block1, []-Hash, Called),
%    write('%%%%% After gen_optimized_code'), nl,
%    print_block(0, N, Block1),
    erase_same_code(0, N, Block1-Block, Hash, Called, []-Same_Labels),
%    write('%%%%% After erase_same_code'), nl,
%    print_block(0, N, Block),
    output_blocks(0, N, Block, Same_Labels, Ltree, NewCode0, []),
    merge_instructions(NewCode0, NewCode, []),
    output_code(1, NewCode).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Routine for giving identical labels to instructions %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- mode give_address_of_labels(+, -, ?, +, +, +).
give_address_of_labels([label(Next)|Rest], 
                       [label(Next)|New0], New1, Pred, L0-L2, T0T1) :- !,
%    write('%%%% First clause '), write(label(Next)), nl,
    give_identical_label(Next, Pred, L0, L1, Flag),
    give_address_of_labels(Rest, New0, New1, Pred, L1-L2, T0T1).
give_address_of_labels([One|Rest], [One|New0], New1, Pred, L0-L2, T0-T2) :- 
    check_if_labelled_instruction(One, Branch, []), !,
%    write('%%%% Second clause '), write(One), nl,
    give_intern_identical_label(Branch, Pred, L0, L1, T0, T1),
    give_address_of_labels(Rest, New0, New1, Pred, L1-L2, T1-T2).
give_address_of_labels([One|Rest], [One|New0], New1, Pred, L0L1, T0T1) :- !,
%    write('%%%% Third clause '), write(One), nl,
    give_address_of_labels(Rest, New0, New1, Pred, L0L1, T0T1).
give_address_of_labels([], New, New, Pred, L-L, T-T) :- !.
%    write('%%%% Fourth clause '), write('[]'), nl.

:- mode check_if_labelled_instruction(+, -, ?).
check_if_labelled_instruction(label(Next), [Next|Br], Br) :- !.
check_if_labelled_instruction(try_me_else(Next), [Next|Br], Br) :- !.
check_if_labelled_instruction(wait(_,Next), [Next|Br], Br) :- !.
check_if_labelled_instruction(One, Br0, Br1) :- 
    is_branch_instruction(One, Br0-Br1), !.
check_if_labelled_instruction(One, Br0, Br1) :- 
    is_type_check_instruction(One, Br0-Br1), !.
check_if_labelled_instruction(One, [Label|Br], Br) :- 
    is_guard_builtin(One, Label), !.

:- mode give_intern_identical_label(+, +, +, -, +, -).
give_intern_identical_label([One|Branch], Pred, L0, L2, T0, T2) :- 
    give_identical_label(One, Pred, L0, L1, Flag),
    intern_if_label_given(Flag, Pred/L0, T0, T1), !,
    give_intern_identical_label(Branch, Pred, L1, L2, T1, T2).
give_intern_identical_label([], _, L, L, T, T) :- !.        

:- mode intern_if_label_given(+, +, +, -).
intern_if_label_given(yes, Key, T0, T1) :- !,
    update_tree(T0, Key, yes, T1).
intern_if_label_given(_, _, T, T) :- !.

:- mode delete_redundant_labels(+, -, ?, +).
delete_redundant_labels([label(Next)|Rest], 
                        [label(Next)|Code0], Code1, Ltree) :-
    check_if_label_used(Ltree, Next, Res), 
    Res == yes, !,
    delete_redundant_labels(Rest, Code0, Code1, Ltree).
delete_redundant_labels([label(Next)|Rest], Code0, Code1, Ltree) :- !,
    delete_redundant_labels(Rest, Code0, Code1, Ltree).
delete_redundant_labels([One|Rest], [One|Code0], Code1, Ltree) :- !,
    delete_redundant_labels(Rest, Code0, Code1, Ltree).
delete_redundant_labels([], Code, Code, Ltree) :- !.

:- mode check_if_label_used(+, ?, -).
check_if_label_used(Ltree, Next, yes) :- nonvar(Next),
    get_tree(Ltree, Next, Res),
    Res == yes, !.
check_if_label_used(Ltree, Next, no) :- var(Next), !,
    error('Illegal key in check_if_label_used: ~w', [Next]).
check_if_label_used(Ltree, Next, no) :- !.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Routine for merging instructions %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

:- mode merge_instructions(+, -, ?).
merge_instructions([One|Code], MrgdCode0, MrgdCode2) :-
    can_be_modified(One, Type), !,
    do_modification(Type, [One|Code], Rest, MrgdCode0, MrgdCode1),
    merge_instructions(Rest, MrgdCode1, MrgdCode2).
merge_instructions([One|Code], [One|MrgdCode0], MrgdCode1) :- !,
    merge_instructions(Code, MrgdCode0, MrgdCode1).
merge_instructions([], MrgdCode, MrgdCode) :- !.

:- mode can_be_modified(+, -).
can_be_modified(try_me_else(_), try_me_else) :- !.
can_be_modified(void_list(_,_), void) :- !.
can_be_modified(void_vector(_,_,_), void) :- !.
can_be_modified(switch_on_type(_,_,_,_,_,_,_), switch) :- !.
can_be_modified(wait(_,_), (wait)) :- !.
can_be_modified(is_atom(_,_), is_instruction) :- !.
can_be_modified(is_integer(_,_), is_instruction) :- !.
can_be_modified(is_float(_,_), is_instruction) :- !.	% 890404 Nishizaki
can_be_modified(is_list(_,_), is_instruction) :- !.
can_be_modified(is_vector(_,_), is_instruction) :- !.
can_be_modified(is_string(_,_), is_instruction) :- !.
can_be_modified(One, guard_builtin) :- is_guard_builtin(One, _), !.
can_be_modified(One, branch_instruction) :-
    is_branch_instruction(One, Branch-[]), !.
can_be_modified(One, type_check_instruction) :-
    is_type_check_instruction(One, Label-[]), !.

:- mode do_modification(+, +, -, -, ?).
do_modification(try_me_else, [One|Code], Code, [One|Mrgd], Mrgd) :- !.
do_modification(void, [_|Code], Code, Mrgd, Mrgd) :- !.
do_modification(switch, Code, Rest, Mrgd0, Mrgd1) :-
    optimize_switch_on_type(Code, Rest, Mrgd0, Mrgd1), !.
do_modification((wait), [wait(A,Fl)|Code], Rest, Mrgd0, Mrgd1) :-
    merge_from_wait_inst(Code, A, Fl, Rest, Mrgd0, Mrgd1), !.
do_modification(is_instruction, Code, Rest, Mrgd0, Mrgd1) :-
    merge_from_is_inst(Code, Rest, Mrgd0, Mrgd1), !.
do_modification(guard_builtin, Code, Rest, Mrgd0, Mrgd1) :- 
    merge_from_guard_builtin(Code, Rest, Mrgd0, Mrgd1), !.
do_modification(_, [One|Code], Code, [One|Mrgd], Mrgd) :- !.

:- mode optimize_switch_on_type(+, -, -, ?).
optimize_switch_on_type([switch_on_type(Ai,A,I,L,V,S,F),label(Lab)|Code], 
                        [New|Code], MrgdCode, MrgdCode) :-
    condense_label(Lab,A,I,L,V,S,F,Ai, New), !.
optimize_switch_on_type([switch_on_type(Ai,A,I,L,V,S,F),label(Lab)|Code], 
	                Code, 
			[switch_on_type(Ai,A,I,L,V,S,F),label(Lab)|MrgdCode], 
			MrgdCode) :- !.

:- mode condense_label(+,+,+,+,+,+,+,+,-).
condense_label(Al,Al,Fl,Fl,Fl,Fl,Fl,Ai, is_atom(Ai,Fl)) :- !.
condense_label(Il,Fl,Il,Fl,Fl,Fl,Fl,Ai, is_integer(Ai,Fl)) :- !.
condense_label(Ll,Fl,Fl,Ll,Fl,Fl,Fl,Ai, is_list(Ai,Ll)) :- !.
condense_label(Vl,Fl,Fl,Fl,Vl,Fl,Fl,Ai, is_vector(Ai,Fl)) :- !.
condense_label(Sl,Fl,Fl,Fl,Fl,Sl,Fl,Ai, is_string(Ai,Fl)) :- !.

:- mode give_identical_label(?, +, +, -, -).
give_identical_label(One, Pred, L0, L1, yes) :-
    var(One), !, One = Pred/L0, L1 is L0+1.
give_identical_label(One, Pred, L, L, no) :- !.

:- mode merge_from_wait_inst(+, +, +, -, -, ?).
/*** ATOM ***/
merge_from_wait_inst([is_atom(A,Fl),test_constant(C,A,Fl)|Code], 
                     A, Fl, Code, 
		     [wait_constant(C,A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_atom(A,Fl),test_constant(C,A,Next)|Code], 
	             A, Fl, Code,
		     [atom(A,Fl),test_constant(C,A,Next)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_atom(A,Fl)|Code], 
                     A, Fl, Code,
		     [atom(A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_atom(A,Next)|Code], 
                     A, Fl, Code,
		     [jump_on_non_atom(A,Next)|Mrgd], Mrgd) :- !.
/*** INTEGER ***/
merge_from_wait_inst([is_integer(A,Fl),test_constant(C,A,Fl)|Code], 
                     A, Fl, Code,
		     [wait_constant(C,A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_integer(A,Fl),test_constant(C,A,Next)|Code], 
                     A, Fl, Code,
		     [integer(A),test_constant(C,A,Next)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_integer(A,Fl)|Code], 
	             A, Fl, Code,
		     [integer(A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_integer(A,Next)|Code], 
	             A, Fl, Code,
		     [jump_on_non_integer(A,Next)|Mrgd], Mrgd) :- !.
/*** FLOAT ***/		% 890404 Nishizaki
merge_from_wait_inst([is_float(A,Fl),test_constant(C,A,Fl)|Code], 
                     A, Fl, Code,
		     [wait_constant(C,A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_float(A,Fl),test_constant(C,A,Next)|Code], 
                     A, Fl, Code,
		     [float(A),test_constant(C,A,Next)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_float(A,Fl)|Code], 
	             A, Fl, Code,
		     [float(A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_float(A,Next)|Code], 
	             A, Fl, Code,
		     [jump_on_non_float(A,Next)|Mrgd], Mrgd) :- !.
/*** LIST ***/
merge_from_wait_inst([is_list(A,Fl)|Code], A, Fl, Code,
		     [wait_list(A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_list(A,Next)|Code], A, Fl, Code,
		     [jump_on_non_list(A,Next)|Mrgd], Mrgd) :- !.
/*** VECTOR ***/
merge_from_wait_inst([is_vector(A,Fl),test_arity(C,A,Fl)|Code], 
                     A, Fl, Code, 
		     [wait_vector(A,C)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_vector(A,Fl)|Code], 
                     A, Fl, Code,
		     [deref_vector(A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_vector(A,Next)|Code], 
                     A, Fl, Code,
		     [jump_on_non_vector(A,Next)|Mrgd], Mrgd) :- !.
/*** STRING ***/
merge_from_wait_inst([is_string(A,Fl)|Code], A, Fl, Code,
		     [wait_string(A,Fl)|Mrgd], Mrgd) :- !.
merge_from_wait_inst([is_string(A,Next)|Code], A, Fl, Code,
		     [jump_on_non_string(A,Next)|Mrgd], Mrgd) :- !.

:- mode merge_from_is_inst(+, -, -, ?).
merge_from_is_inst([is_atom(A,Fl),test_constant(C,A,Fl)|Code], Code,
	           [check_constant(C,A,Fl)|Mrgd], Mrgd) :- !.
merge_from_is_inst([is_integer(A,Fl),test_constant(C,A,Fl)|Code], Code,
	           [check_constant(C,A,Fl)|Mrgd], Mrgd) :- !.
merge_from_is_inst([is_float(A,Fl),test_constant(C,A,Fl)|Code], Code, % 890404 
	           [check_constant(C,A,Fl)|Mrgd], Mrgd) :- !.	    % Nishizaki
merge_from_is_inst([is_vector(A,Fl),test_arity(Arity,A,Fl)|Code], Code,
	           [check_vector(Arity,A,Fl)|Mrgd], Mrgd) :- !.

:- mode merge_from_guard_builtin(+, -, -, ?).
merge_from_guard_builtin([check(wait(Ai,Fl)),check(X)|Code], Code, 
                         [X|Mrgd], Mrgd) :- 
    merge_check_instructions(X, Ai, Fl), !.
merge_from_guard_builtin([check(wait(Ai,Fl)),check(X)|Code], Code, 
                         [wait(Ai,Fl),New|Mrgd], Mrgd) :- 
    change_check_instructions(X, New), !.

:- mode merge_check_instructions(+, +, +).
merge_check_instructions(integer(Ai,Fl), Ai, Fl) :- !.
merge_check_instructions(float(Ai,Fl), Ai, Fl) :- !.	% 890404 Nishizaki
merge_check_instructions(atom(Ai,Fl), Ai, Fl) :- !.
merge_check_instructions(list(Ai,Fl), Ai, Fl) :- !.
merge_check_instructions(vector(Ai,Fl), Ai, Fl) :- !.
merge_check_instructions(string(Ai,Fl), Ai, Fl) :- !.

:- mode change_check_instructions(+, -).
change_check_instructions(integer(Ai,Fl), is_integer(Ai,Fl)) :- !.
change_check_instructions(float(Ai,Fl), is_float(Ai,Fl)) :- !. % Nishizaki
change_check_instructions(atom(Ai,Fl), is_atom(Ai,Fl)) :- !.
change_check_instructions(list(Ai,Fl), is_list(Ai,Fl)) :- !.
change_check_instructions(vector(Ai,Fl), is_vector(Ai,Fl)) :- !.
change_check_instructions(string(Ai,Fl), is_string(Ai,Fl)) :- !.

%%%%%%%%%%%%%%%%%%%%%
% Create_block_list %
%%%%%%%%%%%%%%%%%%%%%

:- mode create_block_list(+, +, +, +, +, +).
create_block_list([], N-N, Pred, L-L, Called-Called, Block-Block) :- !.
create_block_list(Code, N0-N2, Pred, L0-L2, Called0-Called, Block0-Block) :-
    create_one_block(Code, Rest, N0, Pred, L0-L1, 
                     Called0-Called1, Block0-Block1),
    N1 is N0+1,
    create_block_list(Rest, N1-N2, Pred, L1-L2, Called1-Called, Block1-Block).

:- mode create_one_block(+, -, +, +, +, +, +).
create_one_block(Code, Rest, N, Pred, L0L1, Called0-Called1, Block0-Block1) :-
    divide_code(Code, Rest, OneCode, [], Acp, Label, 
                                         Pred, L0L1, BranchList-[]),
    create_block_template(N, OneCode, Label, Acp, OneBlock),
    set_called_label(BranchList, N, Called0, Called1),
    set_one_block(Block0, N, OneBlock, Block1).

:- mode divide_code(+, -, -, ?, ?, ?, +, +, +).
divide_code([], [], New, New, through, Label, _, L-L, Branch-Branch) :- !.
divide_code([label(Label),try_me_else(Fail)|Cdr], Rest, 
            [try_me_else(Fail)|New0], New1, Fail, Label, Pred, L0L1, 
            [Fail|Br0]-Br1) :- !,
    divide_code_1(Cdr, Rest, New0, New1, Pred, L0L1, Br0-Br1).
divide_code([label(Label)|Cdr], Rest, New0, New1, through, Label, 
            Pred, L0L1, BRANCH) :- !,
    divide_code_1(Cdr, Rest, New0, New1, Pred, L0L1, BRANCH).
divide_code([One|Cdr], Rest, [One|New0], New1, ACP, Label, 
            Pred, L0L1, BRANCH) :- !,
    divide_code(Cdr, Rest, New0, New1, ACP, Label, Pred, L0L1, BRANCH).

:- mode divide_code_1(+, -, -, ?, +, +, +).
divide_code_1([], [], New, New, _, L-L, Branch-Branch) :- !.
divide_code_1([label(Lab)|Rest], [label(Lab)|Rest], 
              New, New, _, L-L, Branch-Branch) :- !.
divide_code_1([try_me_else(Fail)|Rest], 
              [label(Pred/L0),try_me_else(Fail)|Rest], 
	      New, New, Pred, L0-L1, 
	      [Pred/L0|Branch]-Branch) :- !,
    L1 is L0+1.
divide_code_1([One|Rest], Rest, [One|New], New, Pred, L-L, BRANCH) :- 
    is_branch_instruction(One, BRANCH), !.
divide_code_1([One|Rest], [label(Pred/L0)|Rest], 
              [One|New], New, Pred, L0-L1, [Pred/L0|Br0]-Br1) :- 
    is_type_check_instruction(One, Br0-Br1), !,
    L1 is L0+1.
divide_code_1([One|Cdr], Rest, [One|New0], New1, Pred, L0L1, BRANCH) :- 
    divide_code_1(Cdr, Rest, New0, New1, Pred, L0L1, BRANCH).

:- mode is_label(+, ?).
is_label(label(Lab), Lab) :- !.

:- mode is_try_me_else(+, ?).
is_try_me_else(try_me_else(Acp), Acp) :- !.

:- mode is_branch_instruction(+, +).
is_branch_instruction(execute(_), Branch-Branch) :- !.
is_branch_instruction(proceed,    Branch-Branch) :- !.
is_branch_instruction(switch_on_type(_, A1,A2,A3,A4,A5,A6),
                                       [A1,A2,A3,A4,A5,A6|B]-B) :- !.
is_branch_instruction(branch_on_constant(_, ConstantList), Br0-Br1) :- !,
    generate_branch_list(ConstantList, Br0, Br1).
is_branch_instruction(branch_on_arity(_, ArityList), Br0-Br1) :- !,
    generate_branch_list(ArityList, Br0, Br1).

:- mode generate_branch_list(+, -, ?).
generate_branch_list([One|Cdr], [One|Branch0], Branch1) :- var(One), !,
    generate_branch_list(Cdr, Branch0, Branch1).
generate_branch_list([(_,L)|Cdr], [L|Branch0], Branch1) :- !,
    generate_branch_list(Cdr, Branch0, Branch1).
generate_branch_list([One|Cdr], [One|Branch0], Branch1) :- 
    One = Pred/A/L, !,
    generate_branch_list(Cdr, Branch0, Branch1).
generate_branch_list([], Branch, Branch) :- !.

:- mode is_type_check_instruction(+, +).
is_type_check_instruction(is_atom(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(is_integer(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(is_float(_,L), [L|Br]-Br) :- !.    % 890404 Nishizaki
is_type_check_instruction(is_list(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(is_vector(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(is_string(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(jump_on_non_atom(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(jump_on_non_integer(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(jump_on_non_float(_,L), [L|Br]-Br) :- !. % Nishizaki
is_type_check_instruction(jump_on_non_list(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(jump_on_non_vector(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(jump_on_non_string(_,L), [L|Br]-Br) :- !.
is_type_check_instruction(test_constant(_,_,L), [L|Br]-Br) :- !.
is_type_check_instruction(test_arity(_,_,L), [L|Br]-Br) :- !.
is_type_check_instruction(check_constant(_,_,L), [L|Br]-Br) :- !.
is_type_check_instruction(check_vector(_,_,L), [L|Br]-Br) :- !.

:- mode is_guard_builtin(+, ?).
is_guard_builtin(One, Label) :- functor(One, F, A),
  ( F == compare, !; F == check ), 
    arg(1, One, Blt), functor(Blt, Name, Arity),
    arg(Arity, Blt, Label).

:- mode get_called_label(+, +, ?).
get_called_label(Tree, N, Label) :- 
    get_tree(Tree, N, Label).

:- mode set_called_label(+, +, +, -).
set_called_label([], _, Called, Called) :- !.
set_called_label([One|BranchList], N, Called0, Called2) :- !,
    intern(Called0, One, N, Called1),
    set_called_label(BranchList, N, Called1, Called2).

%%%%% Generation of optimized codes

:- mode gen_optimized_code(+, +, +, +, +).
gen_optimized_code(N, N, Block-Block, Hash-Hash, Called) :- !.
gen_optimized_code(N0, N2, Block0-Block2, Hash0-Hash2, Called) :-
    get_one_block(Block0, N0, OneBlock),
    optimize_one_block(N0, OneBlock, NewBlock, Block0, Hash0-Hash1, Called),
    set_one_block(Block0, N0, NewBlock, Block1),
    N1 is N0+1,
    gen_optimized_code(N1, N2, Block1-Block2, Hash1-Hash2, Called).

:- mode optimize_one_block(+, +, -, +, +, +).
optimize_one_block(N, OneBlock, [], _, Hash-Hash, Called) :- 
    N \== 0,
    erase_nocall_block(OneBlock, Called), !.
optimize_one_block(N, OneBlock, NewBlock, Block0, Hash0-Hash1, Called) :- 
    erase_extra_try_me_else(OneBlock, NewBlock0, Block0, Called),
    calculate_hash(NewBlock0, HashValue),
    set_block_hash(NewBlock0, HashValue, NewBlock),
    intern(Hash0, HashValue, N, Hash1).
    
:- mode erase_nocall_block(+, +).
erase_nocall_block(OneBlock, _) :- 
    get_block_label(OneBlock, []), !.
erase_nocall_block(OneBlock, Called) :- 
    get_block_label(OneBlock, Label), 
    get_called_label(Called, Label, Called_block), 
    Called_block == [], !.
    
:- mode erase_extra_try_me_else(+, -, +, +).
erase_extra_try_me_else(OneBlock, NewBlock, Block, Called) :- 
    get_block_label(OneBlock, Label),
    get_called_label(Called, Label, Parents),
    calculate_parents_Acp(Parents, Block, Called, Acp0, []),
    sort(Acp0, Acp1), sort_1(Acp1, Acp),
    get_block_code(OneBlock, OneCode),
    delete_same_acp(OneCode, Acp, NewCode0, 0-Length0, 0-Use_try),
    check_if_try_me_else_is_used(Use_try, OneBlock, NewOneBlock,   % Nishizaki
				 NewCode0, NewCode, Length0, Length),
    set_block_code(NewOneBlock, NewCode, NewBlock0),
    set_block_code_length(NewBlock0, Length, NewBlock).

:- mode calculate_parents_Acp(+, +, +, -, ?).
calculate_parents_Acp([], _, _, Acp, Acp) :- !.
calculate_parents_Acp([One|Parents], Block, Called, Acp0, Acp2) :-
    get_one_block(Block, One, OneBlock), OneBlock \== [], !,
    get_block_acp(OneBlock, OneAcp),
  ( OneAcp == through, !, 
	get_block_label(OneBlock, Label),
	get_called_label(Called, Label, GrandParents),
	calculate_parents_Acp(GrandParents, Block, Called, Acp0, Acp1) ;
    Acp0 = [OneAcp|Acp1] ),
    calculate_parents_Acp(Parents, Block, Called, Acp1, Acp2).
calculate_parents_Acp([_|Parents], Block, Called, Acp0, Acp1) :-
    calculate_parents_Acp(Parents, Block, Called, Acp0, Acp1).
    
:- mode delete_same_acp(+, +, -, +, +).
delete_same_acp([], Acp, [], N-N, F-F) :- !.
delete_same_acp([try_me_else(L)|Code], [L], Code, N0N1, FLG) :- !,
    calculate_code_length(Code, N0N1, FLG).
delete_same_acp(Code, Acp, Code, N0N1, FLG) :-
    calculate_code_length(Code, N0N1, FLG).

:- mode calculate_code_length(+, +, +).
calculate_code_length([One|Code], N0-N2, F0-F2) :- 
    N1 is N0+1,
    check_if_branch_inst(One, F0, F1), !,
    calculate_code_length(Code, N1-N2, F1-F2).
calculate_code_length([], N-N, F-F) :- !.

:- mode check_if_branch_inst(+, +, -).
check_if_branch_inst(One, _, 1) :- is_labeled_code(One), !.
check_if_branch_inst(_,   F, F) :- !.

:- mode check_if_try_me_else_is_used(+, +, -, +, -, +, -).
check_if_try_me_else_is_used(0, Block, NewBlock,	% 890413 Nishizaki
				[try_me_else(_)|NewCode], 
	                        NewCode, Length0, Length) :- !,
    set_block_acp(Block, through, NewBlock),		% 890413 Nishizaki
    Length is Length0-1.
check_if_try_me_else_is_used(_, Block, Block, NewCode, NewCode, Length, Length) :- !.

:- mode calculate_hash(+, -).
calculate_hash(NewBlock, HashValue) :- 
    get_block_code_length(NewBlock, Length),
    get_block_code(NewBlock, Code),
    gen_hash_value(Code, Length, 0, HashValue).

:- mode gen_hash_value(+, +, +, -).
gen_hash_value(One, N0, Hv, Hv) :- N0 > 5, !.
gen_hash_value(One, N0, Hv0, Hv1) :-
    hash_code(One, HashValue0),
    Hv1 is Hv0 + HashValue0 + N0.    

:- mode erase_same_code(+, +, +, +, +, +).   /* 88.09.13. Y.Kimura */
erase_same_code(_, _, Block-Block, _, _, Labels-Labels) :- !.

/*******
:- mode erase_same_code(+, +, +, +, +, +).
erase_same_code(N, N, Block-Block, _, _, Labels-Labels) :- !.
erase_same_code(N0, N2, Block0-Block, Hash, Called, LABELS) :-
    is_deleted_block(Block0, N0), !,
    N1 is N0+1,
    erase_same_code(N1, N2, Block0-Block, Hash, Called, LABELS).
erase_same_code(N0, N2, Block0-Block2, Hash, Called, Labels0-Labels2) :-
    is_same_codes(N0, Hash, Block0, SmallestB, Same), !,
    get_one_block(Block0, SmallestB, SmallestBlock),
    get_block_label(SmallestBlock, SmallestLabel),
    set_same_labels(Same, SmallestLabel, Block0, Labels0, Labels1),
    delete_same_blocks(Same, Block0, Block1),
    N1 is N0+1,
    erase_same_code(N1, N2, Block1-Block2, Hash, Called, Labels1-Labels2).
erase_same_code(N0, N2, BLOCK, Hash, Called, LABELS) :-
    N1 is N0+1,
    erase_same_code(N1, N2, BLOCK, Hash, Called, LABELS).
*****/

:- mode is_deleted_block(+, +).
is_deleted_block(Block, N) :- 
    get_tree(Block, N, One), One = [], !.

:- mode is_same_codes(+, +, +, -, -).
is_same_codes(N, Hash, Block, SmallestB, Same) :-
    get_one_block(Block, N, OneBlock),
    get_block_hash(OneBlock, HashValue0),
    get_tree(Hash, HashValue0, CollideList), 
    CollideList = [A,B|Cdr],
    get_block_code(OneBlock, OneCode),
    is_last_instruction_execute_or_proceed(OneCode),
    get_block_code_length(OneBlock, Length),
    is_really_same([A,B|Cdr], Length, OneCode, Block, Collide, []),
    Collide = [_,_|_], !,
    sort(Collide, Collide1), sort_1(Collide1, [SmallestB|Same]).

:- mode is_last_instruction_execute_or_proceed(+).
is_last_instruction_execute_or_proceed([proceed]) :- !.
is_last_instruction_execute_or_proceed([execute(_)]) :- !.
is_last_instruction_execute_or_proceed([_|OneCode]) :- 
    is_last_instruction_execute_or_proceed(OneCode).

:- mode is_really_same(+, +, +, +, -, ?).
is_really_same([], _, _, _, Cold, Cold) :- !.
is_really_same([One|Cdr], Length, OneCode, Block, [One|Cold0], Cold1) :- 
    get_one_block(Block, One, OneBlock),
    get_block_code_length(OneBlock, Length),
    get_block_code(OneBlock, OneCode), !,
    is_really_same(Cdr, Length, OneCode, Block, Cold0, Cold1).
is_really_same([_|Cdr], Length, OneCode, Block, Cold0, Cold1) :- 
    is_really_same(Cdr, Length, OneCode, Block, Cold0, Cold1).

:- mode set_same_labels(+, +, +, +, -).
set_same_labels([], _, Block, Labels, Labels) :- !.
set_same_labels([SmallestL|Same], SmallestL, Block, Labels0, Labels1) :- !,
    set_same_labels(Same, SmallestL, Block, Labels0, Labels1).
set_same_labels([One|Same], SmallestL, Block, Labels0, Labels2) :- !,
    get_one_block(Block, One, OneBlock),
    get_block_label(OneBlock, OneLabel),
    update_tree(Labels0, OneLabel, SmallestL, Labels1),
    set_same_labels(Same, SmallestL, Block, Labels1, Labels2).

:- mode delete_same_blocks(+, +, -).
delete_same_blocks([], Block, Block) :- !.
delete_same_blocks([N|Same], Block0, Block2) :- 
    set_one_block(Block0, N, [], Block1),
    delete_same_blocks(Same, Block1, Block2).

:- mode output_blocks(+, +, +, +, +, -, ?).
output_blocks(N, N, Block, Same_Labels, Ltree, Code, Code) :- !.
output_blocks(I, N, Block, Same_Labels, Ltree, Code0, Code3) :- 
    get_one_block(Block, I, OneBlock), OneBlock \== [], !,
    get_block_label(OneBlock, Label), 
    check_if_label_can_be_deleted(Ltree, Label, Code0, Code1),
    get_block_code(OneBlock, Code),
    append_block_code(Code, Code1, Code2), 
    I1 is I+1,
    output_blocks(I1, N, Block, Same_Labels, Ltree, Code2, Code3).
output_blocks(I, N, Block, Same_Labels, Ltree, Code0, Code1) :-
    I1 is I+1,
    output_blocks(I1, N, Block, Same_Labels, Ltree, Code0, Code1).

:- mode check_if_label_can_be_deleted(+, +, -, ?).
check_if_label_can_be_deleted(Ltree, Label, [label(Label)|Code], Code) :-
    get_tree(Ltree, Label, Res), Res == yes, !.
check_if_label_can_be_deleted(Ltree, Label, Code, Code) :- !.

:- mode append_block_code(+, -, ?).
append_block_code([One|Code], [One|New0], New1) :- !,
    append_block_code(Code, New0, New1).
append_block_code([], Code, Code) :- !.

:- mode is_labeled_code(+).
is_labeled_code(jump_on_non_atom(_,_)) :- !.
is_labeled_code(jump_on_non_integer(_,_)) :- !.
is_labeled_code(jump_on_non_float(_,_)) :- !.	% 890404 Nishizaki
is_labeled_code(jump_on_non_list(_,_)) :- !.
is_labeled_code(jump_on_non_vector(_,_)) :- !.
is_labeled_code(jump_on_non_string(_,_)) :- !.
is_labeled_code(wait(_,_)) :- !.
is_labeled_code(wait_list(_,_)) :- !.
is_labeled_code(wait_vector(_,_,_)) :- !.
is_labeled_code(wait_constant(_,_,_)) :- !.
is_labeled_code(wait_value(_,_,_)) :- !.
is_labeled_code(wait_string(_,_)) :- !.
is_labeled_code(atom(_,_)) :- !.
is_labeled_code(integer(_,_)) :- !.
is_labeled_code(float(_,_)) :- !.	% 890404 Nishizaki
is_labeled_code(list(_,_)) :- !.
is_labeled_code(deref_vector(_,_)) :- !.
is_labeled_code(vector(_,_/_)) :- !.
is_labeled_code(string(_,_)) :- !.
is_labeled_code(Blt) :- functor(Blt, F, _),
  ( F == compare, ! ; F == check, ! ; F == branch ), !. % 890605 Nishizaki

:- mode convert_optimized_labeled_code(+, -, +).
convert_optimized_labeled_code(try_me_else(L), 
                               try_me_else(LL), Labels) :- !, 
    find_new_label(Labels, L, LL).
convert_optimized_labeled_code(wait(A,L), wait(A,LL),  Labels) :- !, 
    find_new_label(Labels, L, LL).
convert_optimized_labeled_code(wait_constant(C,A,L), 
                               wait_constant(C,A,LL),  Labels) :- !, 
    find_new_label(Labels, L, LL).
convert_optimized_labeled_code(test_constant(C,A,L), 
                               test_constant(C,A,LL),  Labels) :- !, 
    find_new_label(Labels, L, LL).
convert_optimized_labeled_code(wait_value(C,A,L), 
                               wait_value(C,A,LL),  Labels) :- !, 
    find_new_label(Labels, L, LL).
convert_optimized_labeled_code(test_arity(C,A,L), 
                               test_arity(C,A,LL),  Labels) :- !, 
    find_new_label(Labels, L, LL).
convert_optimized_labeled_code(switch_on_type(R,A1,A2,A3,A4,A5,A6),
                               New_Inst, Labels) :- !, 
    find_new_label_loop([A1,A2,A3,A4,A5,A6], Lab_List, [], Labels),
    New_Inst =.. [switch_on_type,R|Lab_List].
convert_optimized_labeled_code(branch_on_constant(R, Labels_List),
                               branch_on_constant(R, New_List),
                               Labels) :- !, 
    extract_labels_from(Labels_List, Branch_List, []),
    find_new_label_loop(Branch_List, Branch_New, [], Labels),
    reconstruct_labels_list(Branch_New, Labels_List, New_List, []).
convert_optimized_labeled_code(branch_on_arity(R, Labels_List),
                               branch_on_arity(R, New_List),
                               Labels) :- !, 
    extract_labels_from(Labels_List, Branch_List, []),
    find_new_label_loop(Branch_List, Branch_New, [], Labels),
    reconstruct_labels_list(Branch_New, Labels_List, New_List, []).
convert_optimized_labeled_code(BLT, NewBLT, Labels) :-
    functor(BLT, F, A),
    arg(A, BLT, L), find_new_label(Labels, L, LL),
    copy_builtin_code(A, BLT, NewBLT, LL).
    
:- mode copy_builtin_code(+, +, -, +).
copy_builtin_code(2, BLT, NewBLT, LL) :- !,
    BLT =.. [F,A|_], NewBLT =.. [F,A,LL].
copy_builtin_code(3, BLT, NewBLT, LL) :- !,
    BLT =.. [F,A,B|_], NewBLT =.. [F,A,B,LL].

:- mode extract_labels_from(+, -, ?).
extract_labels_from([F/A/B], [(F/A/B)|Branch_List], Branch_List) :- !.
extract_labels_from([(_,V)|Labels_List], [V|Branch_List0], Branch_List1) :-
    extract_labels_from(Labels_List, Branch_List0, Branch_List1).

:- mode find_new_label_loop(+, -, ?, +).
find_new_label_loop([], Branch_New, Branch_New, Labels) :- !.
find_new_label_loop([One|Branch_List], 
                    [New|Branch_New0], Branch_New1, Labels) :- 
    find_new_label(Labels, One, New), 
    find_new_label_loop(Branch_List, Branch_New0, Branch_New1, Labels).

:- mode find_new_label(+, +, -).
find_new_label(Labels, L, LL) :- 
    get_tree(Labels, L, LL), 
    LL \== [], !.
find_new_label(_, L, L) :- !.

:- mode reconstruct_labels_list(+, +, -, ?).
reconstruct_labels_list([F/A/B], [F/A/C], [F/A/B|New_List], New_List) :- !.
reconstruct_labels_list([One|Branch_New], [(L,_)|Labels_List], 
                        [(L,One)|New_List0], New_List1) :-
    reconstruct_labels_list(Branch_New, Labels_List, New_List0, New_List1).

%%%%% Code Block Manipulation

:- mode get_one_block(+, +, ?).
get_one_block(Tree, Key, Block) :- get_tree(Tree, Key, Block).

:- mode set_one_block(+, +, ?, -).
set_one_block(Tree, Key, Block, New) :- 
    update_tree(Tree, Key, Block, New).

:- mode create_block_template(+, +, +, +, -).
create_block_template(N, OneCode, Label, Acp, OneBlock) :-
    array(7, OneBlock0),
    aset(OneBlock0, 0, N,       OneBlock1),
    aset(OneBlock1, 1, OneCode, OneBlock2),
    aset(OneBlock2, 2, Label,   OneBlock3),
    aset(OneBlock3, 3, Acp,     OneBlock4),
    aset(OneBlock4, 4, 0,       OneBlock5),
    aset(OneBlock5, 5, 0,       OneBlock).

:- mode get_block_no(+, ?).
get_block_no(Block, N) :- aref(Block, 0, N).

:- mode get_block_code(+, ?).
get_block_code(Block, Code) :- aref(Block, 1, Code).

:- mode get_block_label(+, ?).
get_block_label(Block, Label) :- aref(Block, 2, Label).

:- mode get_block_acp(+, ?).
get_block_acp(Block, Acp) :- aref(Block, 3, Acp).

:- mode get_block_hash(+, ?).
get_block_hash(Block, Hash) :- aref(Block, 4, Hash).

:- mode get_block_code_length(+, ?).
get_block_code_length(Block, Length) :- aref(Block, 5, Length).

:- mode set_block_no(+, ?, -).
set_block_no(Block0, N, Block) :- 
    aset(Block0, 0, N, Block).

:- mode set_block_code(+, ?, -).
set_block_code(Block0, Code, Block) :- 
    aset(Block0, 1, Code, Block).

:- mode set_block_label(+, ?, -).
set_block_label(Block0, Label, Block) :- 
    aset(Block0, 2, Label, Block).

:- mode set_block_acp(+, ?, -).
set_block_acp(Block0, Acp, Block) :- 
    aset(Block0, 3, Acp, Block).

:- mode set_block_hash(+, ?, -).
set_block_hash(Block0, Hash, Block) :- 
    aset(Block0, 4, Hash, Block).

:- mode set_block_code_length(+, ?, -).
set_block_code_length(Block0, Length, Block) :- 
    aset(Block0, 5, Length, Block).

%%%%% Hash function for one code

:- mode hash_code(+, -).
hash_code(One, Hash) :- integer(One), !, 
    Hash is One /\ 65535.                               % 65536 = 2^16
hash_code(One, Hash) :- float(One), !, 			% 890602 Nishizaki
    hash_float(One, Hash).
hash_code(One, Hash) :- atom(One), !, 
    name(One, List), hash_atom(List, 0, Hash0), 
    Hash is Hash0 /\ 65535.
hash_code(One, Hash) :- functor(One, '.', 2), !, 
    arg(1, One, Car), arg(2, One, Cdr),
    hash_code(Car, Hash0), 
    hash_code(Cdr, Hash1),
    Hash is (Hash0 + Hash1) /\ 65535.
hash_code(One, Hash) :- functor(One, F, A), !, 
    One =.. List, 
    hash_structure(List, 0, Hash0), 
    Hash is Hash0 /\ 65535.

:- mode hash_atom(+, +, -).
hash_atom([], Hash, Hash) :- !.
hash_atom([One|List], Hash0, Hash) :- !,
    Hash1 is (Hash0 + One) /\ 65535,
    hash_atom(List, Hash1, Hash).

:- mode hash_structure(+, +, -).
hash_structure([], Hash, Hash) :- !.
hash_structure([One|List], Hash0, Hash) :- !,
    hash_code(One,  Hash1),
    hash_code(List, Hash2),
    Hash is (Hash0 + Hash1 + Hash2) /\ 65535.

:- mode hash_float(+,-).
hash_float(One, Hash) :- One > 2147483647, !,
	NOne is One / 2.0,
	hash_float(NOne, Hash).
hash_float(One, Hash) :- One < -2147483648, !,
	NOne is One / 2.0,
	hash_float(NOne, Hash).
hash_float(One, Hash) :- !,
	Hash is One /\ 65535.

%%%%% Debug routine

:- mode print_block(+, +, +).
print_block(N, N, _) :- !, nl.
print_block(I, N, Tree) :- get_tree(Tree, I, One),
    write(I), write('  '), write(One), nl,
    I1 is I+1,
    print_block(I1, N, Tree).
