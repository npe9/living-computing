%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% GC OPTION

:- mode gc_option(+, +, -, +, +, -).
gc_option(0, Code, Code, _, TABLE, TABLE) :- !.
gc_option(1, Code0, Code, Aux, From-To0-Gref-Bref0, 
                               From-To-Gref-Bref) :- !,
    mrb_guard(Code0, Body0, Code, Body, Gc_code,
	      0-CommitPC, To0, Bref0-Bref1, Aux, Gc_code-[], Gc-[]), 
    mrb_update_To_table_of_gc_code(Gc_code, CommitPC, To0, To),
    mrb_body(Body0, Body, [], Gref, Bref1-Bref).
gc_option(2, Code0, Code, Aux, From-To0-Gref-Bref0, 
                               From-To-Gref-Bref) :- !,
    mrb_guard(Code0, Body0, Code, Body, Gc_code,
	      0-CommitPC, To0, Bref0-Bref1, Aux, Gc_code-Mk_end, Gc0-[]), 
    sort(Gc0, Mk_end),
    mrb_update_To_table_of_gc_code(Gc_code, CommitPC, To0, To),
    mrb_body(Body0, Body, [], Gref, Bref1-Bref).
gc_option(3, Code0, Code, Aux, From-To0-Gref-Bref0, 
                               From-To-Gref-Bref) :- !,
    mrb_guard(Code0, Body0, Code, Body, Gc_code,
	      0-CommitPC, To0, Bref0-Bref1, Aux, Gc_code0-Mk_end, Gc0-[]), 
    PC1 is CommitPC + 1,
    sort(Gc0, Mk_end),
    mrb_get_reusable_structure_reg(Gc_code0, ReuseReg, []),
    mrb_body_with_reuse_option(Body0, Body, [], PC1, 
                                                ReuseReg,
						UsedReg-[],
						Gref, Bref1-Bref),    
    mrb_update_gc_code(Gc_code0, UsedReg, Gc_code, []),
    mrb_update_To_table_of_reused_reg(UsedReg, To0, To1),
    mrb_update_To_table_of_gc_code(Gc_code, CommitPC, To1, To).

:- mode mrb_guard(+, -, -, -, -, +, +, +, +, +, +). 
mrb_guard([commit|Body], Body, ['$GC_CODE'(Gc_code)|Code], Code,
	  Gc_code, PC-PC, _, Bref-Bref, _, Mk-Mk, Gc-Gc) :- !.
mrb_guard([Inst|Next], Body, [Inst|Code0], Code1, 
	  Gc_code, PC0-PC2, To, Bref0-Bref2, Type-Attr, Mk0-Mk2, Gc0-Gc2) :- 
    mrb_mark_check(Inst, Bref0, Bref1, Attr, Mk0-Mk1),
    mrb_gc_check(Inst, (To,PC0), Bref1, Type-Attr, Gc0-Gc1),
    PC1 is PC0+1,
    mrb_guard(Next, Body, Code0, Code1, 
              Gc_code, PC1-PC2, To, Bref1-Bref2, Type-Attr, Mk1-Mk2, Gc1-Gc2).

:- mode mrb_mark_check(+, +, -, +, +).
mrb_mark_check(wait_variable('$VAR'(N),_), Bref0, Bref, Attr0, Mk0-Mk2) :- 
    aref(Bref0, N, C), C > 0, 
    var_no_attr(Attr0, N, ElemList0), 
    sort(ElemList0, ElemList1), sort_1(ElemList1, ElemList),
%    mrb_has_element_attr(ElemList, Attr0, Bref0, ParentC), !,
    mrb_has_element_attr(ElemList, Attr0, Bref0, ParentC, VI), !,
%    mrb_gen_mark_instruction_in_nested_structure(ElemList, Mk0, Mk1),
    mrb_gen_mark_instruction_in_nested_structure(ElemList, Mk0, Mk1, VI),
    mrb_update_Bref(Bref0, N, ParentC, Bref1),
    mrb_mark_arg(ElemList, N, Attr0, Bref1, Bref, Mk1-Mk2).
mrb_mark_check(Inst, Bref0, Bref, Attr0, Mk0Mk1) :-
    mrb_lookup_mark_check_var(Inst, '$VAR'(N)), !,
    var_no_attr(Attr0, N, ElemList0), 
    sort(ElemList0, ElemList1), sort_1(ElemList1, ElemList),
    mrb_mark_arg(ElemList, N, Attr0, Bref0, Bref, Mk0Mk1).
%mrb_mark_check(Inst, Bref0, Bref, Attr0, Mk0Mk1) :-
%    mrb_lookup_element_mark_check_var(Inst, '$VAR'(N)), !,
%    var_no_attr(Attr0, N, ElemList0), 
%    sort(ElemList0, ElemList1), sort_1(ElemList1, ElemList),
%    mrb_mark_element_arg(ElemList, N, Attr0, Bref0, Bref, Mk0Mk1).
mrb_mark_check(_, Bref, Bref, _, Mk-Mk) :- !.

%:- mode mrb_has_element_attr(+, +, +, -).
:- mode mrb_has_element_attr(+, +, +, -, -).
%mrb_has_element_attr([element(V,_)|ElemList], Attr, Bref, C) :- !,
mrb_has_element_attr([element(V,I)|ElemList], Attr, Bref, C, (V,I)) :- !,
    var_no(V, N), aref(Bref, N, C).
%mrb_has_element_attr([vector('$VAR'(N),_)|Cdr], Attr, Bref, C) :-
mrb_has_element_attr([vector('$VAR'(N),_)|Cdr], Attr, Bref, C, VI) :-
    var_no_attr(Attr, N, ElemList0), 
    sort(ElemList0, ElemList1), sort_1(ElemList1, ElemList),
%    mrb_has_element_attr(ElemList, Attr, Bref, C), !.
    mrb_has_element_attr(ElemList, Attr, Bref, C, VI), !.
%mrb_has_element_attr([car('$VAR'(N))|Cdr], Attr, Bref, C) :-
mrb_has_element_attr([car('$VAR'(N))|Cdr], Attr, Bref, C, VI) :-
    var_no_attr(Attr, N, ElemList0), 
    sort(ElemList0, ElemList1), sort_1(ElemList1, ElemList),
%    mrb_has_element_attr(ElemList, Attr, Bref, C), !.
    mrb_has_element_attr(ElemList, Attr, Bref, C, VI), !.
%mrb_has_element_attr([cdr('$VAR'(N))|Cdr], Attr, Bref, C) :-
mrb_has_element_attr([cdr('$VAR'(N))|Cdr], Attr, Bref, C, VI) :-
    var_no_attr(Attr, N, ElemList0), 
    sort(ElemList0, ElemList1), sort_1(ElemList1, ElemList),
%    mrb_has_element_attr(ElemList, Attr, Bref, C), !.
    mrb_has_element_attr(ElemList, Attr, Bref, C, VI), !.
%mrb_has_element_attr([_|ElemList], Attr, Bref, C) :-
mrb_has_element_attr([_|ElemList], Attr, Bref, C, VI) :-
%    mrb_has_element_attr(ElemList, Attr, Bref, C).
    mrb_has_element_attr(ElemList, Attr, Bref, C, VI).

%:- mode mrb_gen_mark_instruction_in_nested_structure(+, -, ?).
:- mode mrb_gen_mark_instruction_in_nested_structure(+, -, ?, +).
mrb_gen_mark_instruction_in_nested_structure([car(V)|_], 
%    [mark_car(V)|Mk], Mk) :- !.
    [mark_element(VV,II)|Mk], Mk, (VV,II)) :- !.
mrb_gen_mark_instruction_in_nested_structure([cdr(V)|_],
%    [mark_cdr(V)|Mk], Mk) :- !.
    [mark_element(VV,II)|Mk], Mk, (VV,II)) :- !.
mrb_gen_mark_instruction_in_nested_structure([vector(V,I)|_],
%    [mark_vector(V,I)|Mk], Mk) :- !.
    [mark_element(VV,II)|Mk], Mk, (VV,II)) :- !.
%mrb_gen_mark_instruction_in_nested_structure([element(V,I)|_], Mk, Mk) :- !.
mrb_gen_mark_instruction_in_nested_structure([element(V,I)|_], Mk, Mk, _) :- !.
%mrb_gen_mark_instruction_in_nested_structure([_|Cdr], Mk0, Mk1) :- !,
%    mrb_gen_mark_instruction_in_nested_structure(Cdr, Mk0, Mk1).
mrb_gen_mark_instruction_in_nested_structure([_|Cdr], Mk0, Mk1, VI) :- !,
    mrb_gen_mark_instruction_in_nested_structure(Cdr, Mk0, Mk1, VI).
%mrb_gen_mark_instruction_in_nested_structure([], Mk, Mk) :- !,
mrb_gen_mark_instruction_in_nested_structure([], Mk, Mk, _) :- !,
    error(
      'Legal attr not found in mrb_gen_mark_instruction_in_nested_structure', 
      []).

:- mode mrb_update_Bref(+, +, +, -).
mrb_update_Bref(Bref0, N, C, Bref1) :- 
    aref(Bref0, N, C0), C1 is C0+C, aset(Bref0, N, C1, Bref1).

:- mode mrb_lookup_mark_check_var(+, ?).
mrb_lookup_mark_check_var(wait_variable(A,_), A) :- !.
mrb_lookup_mark_check_var(wait_value(A,_,_), A) :- !.
mrb_lookup_mark_check_var(read_car(_,A), A) :- !.
mrb_lookup_mark_check_var(read_cdr(_,A), A) :- !.
mrb_lookup_mark_check_var(read_element(_,_,A), A) :- !.

%:- mode mrb_lookup_element_mark_check_var(+, ?).
%mrb_lookup_element_mark_check_var(wait_variable(A,_), A) :- !.
%%mrb_lookup_element_mark_check_var(wait_value(_,A,_), A) :- !.
%mrb_lookup_element_mark_check_var(wait_constant(_,A,_), A) :- !.

:- mode mrb_mark_arg(+, +, +, +, -, +).
mrb_mark_arg([], _, _, Bref, Bref, Mk-Mk) :- !.
mrb_mark_arg([element(V,I)|Cdr], N, Attr, Bref0, Bref2, 
	                            [mark_element(V,I)|Mk0]-Mk1) :-
    aref(Bref0, N, C), C > 0, !,
    mrb_mark_one_arg(Attr, N, Bref0, Bref1),
    mrb_mark_arg(Cdr, N, Attr, Bref1, Bref2, Mk0-Mk1).
mrb_mark_arg([One|Cdr], N, Attr, Bref0, Bref2, Mk0-Mk2) :-
    mrb_is_mark_attribute(One, V, Mk0-Mk1), 
    aref(Bref0, N, Cn), Cn > 0,
    var_no(V, Vn), aref(Bref0, Vn, C), C > 0, !,
    mrb_mark_one_arg(Attr, N, Bref0, Bref1),
    mrb_mark_arg(Cdr, N, Attr, Bref1, Bref2, Mk1-Mk2).
mrb_mark_arg([_|Cdr], N, Attr, Bref0, Bref1, MARK) :-
    mrb_mark_arg(Cdr, N, Attr, Bref0, Bref1, MARK).

:- mode mrb_is_mark_attribute(+, -, +).
mrb_is_mark_attribute(car(V), V, [mark_car(V)|Mk]-Mk) :- !.
mrb_is_mark_attribute(cdr(V), V, [mark_cdr(V)|Mk]-Mk) :- !.
mrb_is_mark_attribute(vector(V,I), V, [mark_element(V,I)|Mk]-Mk) :- !.

%:- mode mrb_mark_element_arg(+, +, +, +, -, +).
%mrb_mark_element_arg([], _, _, Bref, Bref, Mk-Mk) :- !.
%mrb_mark_element_arg([element(V,I)|Cdr], N, Attr, Bref0, Bref2, 
%	                            [mark_element(V,I)|Mk0]-Mk1) :-
%    aref(Bref0, N, C), C > 0, !,
%    mrb_mark_one_arg(Attr, N, Bref0, Bref1),
%    mrb_mark_element_arg(Cdr, N, Attr, Bref1, Bref2, Mk0-Mk1).
%mrb_mark_element_arg([_|Cdr], N, Attr, Bref0, Bref1, MARK) :-
%    mrb_mark_element_arg(Cdr, N, Attr, Bref0, Bref1, MARK).

:- mode mrb_mark_one_arg(+, +, +, -).
mrb_mark_one_arg(Attr, N, Bref0, Bref) :- !,
    var_no_attr(Attr, N, NvAttr),
    aref(Bref0, N, Cv0),
    mrb_modify_refer_by_parents(NvAttr, Attr, Bref0, Cv0, Cv),
    mrb_modify_element_refer(NvAttr, Bref0, Cv, NewC),
    aset(Bref0, N, NewC, Bref).

:- mode mrb_modify_refer_by_parents(+, +, +, +, -).
mrb_modify_refer_by_parents([], _, _, Cv, Cv) :- !.
mrb_modify_refer_by_parents([One|NvAttr], Attr, Bref, Cv0, Cv) :-
    mrb_is_attribute(One, V), !,
    var_no(V, Nv), var_no_attr(Attr, Nv, ParentAttr),
    aref(Bref, Nv, Cv1), Cv2 is Cv0+Cv1,
    mrb_modify_refer_by_parents(ParentAttr, Attr, Bref, Cv2, Cv3),
    mrb_modify_refer_by_parents(NvAttr, Attr, Bref, Cv3, Cv).
mrb_modify_refer_by_parents([_|NvAttr], Attr, Bref, Cv0, Cv) :-
    mrb_modify_refer_by_parents(NvAttr, Attr, Bref, Cv0, Cv).

:- mode mrb_is_attribute(+, -).
mrb_is_attribute(car(V), V) :- !.
mrb_is_attribute(cdr(V), V) :- !.
mrb_is_attribute(vector(V,_), V) :- !.
mrb_is_attribute(element(V,_), V) :- !.

:- mode mrb_modify_element_refer(+, +, +, -).
mrb_modify_element_refer([], _, C, C) :- !.
mrb_modify_element_refer([parent(E)|NvAttr], Bref0, C0, NewC) :- !,
    var_no(E, N), aref(Bref0, N, Ec),
    C1 is C0 + Ec,
    mrb_modify_element_refer(NvAttr, Bref0, C1, NewC).
mrb_modify_element_refer([_|NvAttr], Bref0, C0, NewC) :-
    mrb_modify_element_refer(NvAttr, Bref0, C0, NewC).

:- mode mrb_gc_check(+, +, +, +, +).
mrb_gc_check(wait_list(Ai,L), _, Bref, Type-Attr, 
                                       [collect_list(Ai)|Gc]-Gc) :-
    var_no(Ai,N), 
    aref(Bref, N, C), C =:= 0, 
    aref(Attr, N, OneAttr), 
    mrb_is_var_attr_element(OneAttr, Attr, no, Res),
    Res == no, !.
mrb_gc_check(wait_vector(Ai,No,L), _, Bref, Type-Attr, 
                                      [collect_vector(Ai,No)|Gc]-Gc) :-
    No > 0, var_no(Ai, N), 
    aref(Bref, N, C), C =:= 0,
    aref(Attr, N, OneAttr), 
    mrb_is_var_attr_element(OneAttr, Attr, no, Res), 
    Res == no, !.
mrb_gc_check(void_list(Ai,L), _, Bref, Type-Attr, 
                                       [collect_list(Ai)|Gc]-Gc) :-
    var_no(Ai,N), 
    aref(Bref, N, C), C =:= 0,
    aref(Attr, N, OneAttr), 
    mrb_is_var_attr_element(OneAttr, Attr, no, Res), 
    Res == no, !.
mrb_gc_check(void_vector(Ai,No,L), _, Bref, Type-Attr, 
                                      [collect_vector(Ai,No)|Gc]-Gc) :-
    No > 0, var_no(Ai, N), 
    aref(Bref, N, C), C =:= 0,
    aref(Attr, N, OneAttr), 
    mrb_is_var_attr_element(OneAttr, Attr, no, Res), 
    Res == no, !.
mrb_gc_check(Inst, ToPC, Bref, Aux, GC) :- 
    mrb_void_check(Inst, ToPC, Bref, Aux, GC), !.
mrb_gc_check(Inst, _, _, _, Gc-Gc) :- !.

:- mode mrb_void_check(+, +, +, +, +).
mrb_void_check(calculate(BLT), ToPC, Bref, Aux, GC) :- !,
    builtin(BLT, In, _, _, _, _, _),
    mrb_last_builtin_arg_check(In, ToPC, Bref, Aux, GC, BLT).  
mrb_void_check(branch(BLT), ToPC, Bref, Aux, GC) :- !, % 890605 Nishizaki
    builtin(BLT, In, _, _, _, _, _),
    mrb_last_builtin_arg_check(In, ToPC, Bref, Aux, GC, BLT).  
mrb_void_check(compare(BLT,_), ToPC, Bref, Aux, GC) :- !,
    builtin(BLT, In, _, _, _, _, _),
    mrb_last_builtin_arg_check(In, ToPC, Bref, Aux, GC, BLT).  
mrb_void_check(check(BLT,_), ToPC, Bref, Aux, GC) :- !,
    builtin(BLT, In, _, _, _, _, _),
    mrb_last_builtin_arg_check(In, ToPC, Bref, Aux, GC, BLT).  
mrb_void_check(Inst, ToPC, Bref, Aux, GC) :-
    mrb_is_void_check_inst(Inst, Var_list), !,
    mrb_void_check_loop(Var_list, ToPC, Bref, Aux, GC).
mrb_void_check(_, _, _, _, Gc-Gc) :- !.

:- mode mrb_is_void_check_inst(+, -).
mrb_is_void_check_inst(wait_variable(Ai,Aj), [Ai]) :- !.
mrb_is_void_check_inst(wait_value(Ai,Aj,_),  [Ai,Aj]) :- !.   % 8810013

:- mode mrb_void_check_loop(+, +, +, +, +).                   % 881031
mrb_void_check_loop([Ai,Aj], ToPC, Bref, Aux, Gc0-Gc2) :-
  ( mrb_void_arg_check(Ai, ToPC, Bref, Aux, Gc0-Gc1), !;
      Gc0 = Gc1 ), 
  ( mrb_void_arg_check(Aj, ToPC, Bref, Aux, Gc1-Gc2), !;
      Gc1 = Gc2 ).
mrb_void_check_loop([Ai], ToPC, Bref, Aux, GCs) :-
    mrb_void_arg_check(Ai, ToPC, Bref, Aux, GCs).

:- mode mrb_last_builtin_arg_check(+, +, +, +, +, +).
mrb_last_builtin_arg_check([], _, _, _, Gc-Gc, _) :- !.
mrb_last_builtin_arg_check([One|Cdr], (To,PC), Bref, Type-Attr, 
                                                     Gc0-Gc2, BLT) :-
    arg(One, BLT, '$VAR'(N)), aref(To, N, C), C =< PC,
    var_no_attr(Attr, N, AttrCons),
    mrb_is_var_attr_element(AttrCons, Attr, no, Res),
    mrb_generate_collect_value(Res, N, Bref, Type-Attr, Gc0, Gc1), !,
    mrb_last_builtin_arg_check(Cdr, (To,PC), Bref, Type-Attr, Gc1-Gc2, BLT).
mrb_last_builtin_arg_check([_|Cdr], ToPC, Bref, Aux, GC, BLT) :- !,
    mrb_last_builtin_arg_check(Cdr, ToPC, Bref, Aux, GC, BLT).

:- mode mrb_void_arg_check(+, +, +, +, +).
mrb_void_arg_check('$VAR'(N), (To,PC), Bref, Type-Attr, Gc0-Gc1) :-
    aref(To, N, C), C =< PC,
    var_no_attr(Attr, N, AttrCons),
    mrb_is_var_attr_element(AttrCons, Attr, no, Res),
    mrb_generate_collect_value(Res, N, Bref, Type-Attr, Gc0, Gc1).

:- mode mrb_is_var_attr_element(+, +, +, -).
mrb_is_var_attr_element([], _, Flag, Flag) :- !.
mrb_is_var_attr_element([element(_,_)|AttrCons], _, _, yes) :- !.
mrb_is_var_attr_element([car('$VAR'(N))|Cdr], Attr, Flag0, Flag) :- !,
    aref(Attr, N, OneAttr),
    mrb_is_var_attr_element(OneAttr, Attr, Flag0, Flag1),
    mrb_is_var_attr_element(Cdr, Attr, Flag1, Flag).
mrb_is_var_attr_element([cdr('$VAR'(N))|Cdr], Attr, Flag0, Flag) :- !,
    aref(Attr, N, OneAttr),
    mrb_is_var_attr_element(OneAttr, Attr, Flag0, Flag1),
    mrb_is_var_attr_element(Cdr, Attr, Flag1, Flag).
mrb_is_var_attr_element([vector('$VAR'(N),_)|Cdr], Attr, Flag0, Flag) :- !,
    aref(Attr, N, OneAttr),
    mrb_is_var_attr_element(OneAttr, Attr, Flag0, Flag1),
    mrb_is_var_attr_element(Cdr, Attr, Flag1, Flag).
mrb_is_var_attr_element([_|AttrCons], Attr, Flag, Res) :- !,
    mrb_is_var_attr_element(AttrCons, Attr, Flag, Res).

:- mode mrb_generate_collect_value(+, +, +, +, -, ?).
mrb_generate_collect_value(no, N, _, Type-Attr, Gc, Gc) :- 
    aref(Type, N, Vtype), mrb_not_gen_collect_value(Vtype), !.
mrb_generate_collect_value(no, N, Bref, Type-Attr, Gc, Gc) :-
    aref(Attr, N, Vattr), 
    mrb_is_structure_passed_to_body(Vattr, Bref, no, yes), !.
mrb_generate_collect_value(no, N, _, Type-Attr, Gc, Gc) :-
    aref(Attr, N, Vattr), mrb_is_vector_element(Vattr, Attr, no, Res),
    Res == yes, !.
mrb_generate_collect_value(no, N, _, _, 
                                  [collect_value('$VAR'(N))|Gc], Gc) :- !.
mrb_generate_collect_value(yes, _, _, _, Gc, Gc).

:- mode mrb_not_gen_collect_value(+).
mrb_not_gen_collect_value(integer) :- !.
mrb_not_gen_collect_value(float) :- !.		% 890404 Nishizaki
mrb_not_gen_collect_value(atom) :- !.

:- mode mrb_is_structure_passed_to_body(+, +, +, ?).
mrb_is_structure_passed_to_body([], _, Flag, Flag) :- !.
mrb_is_structure_passed_to_body([car('$VAR'(N))|Vattr], Bref, _, Flag) :- 
    aref(Bref, N, C), C > 0, !,
    mrb_is_structure_passed_to_body(Vattr, Bref, yes, Flag).
mrb_is_structure_passed_to_body([cdr('$VAR'(N))|Vattr], Bref, _, Flag) :- 
    aref(Bref, N, C), C > 0, !,
    mrb_is_structure_passed_to_body(Vattr, Bref, yes, Flag).
mrb_is_structure_passed_to_body([vector('$VAR'(N),_)|Vattr], Bref, _, Flag) :- 
    aref(Bref, N, C), C > 0, !,
    mrb_is_structure_passed_to_body(Vattr, Bref, yes, Flag).
mrb_is_structure_passed_to_body([_|Vattr], Bref, Flag0, Flag1) :- 
    mrb_is_structure_passed_to_body(Vattr, Bref, Flag0, Flag1).

:- mode mrb_is_vector_element(+, +, +, ?).
mrb_is_vector_element([], _, Flag, Flag) :- !.
mrb_is_vector_element([element(_,_)|Vattr], Attr, _, yes) :- !.
mrb_is_vector_element([vector('$VAR'(N),_)|Vattr], Attr, _, yes) :-
    aref(Attr, N, ElemAttr0),
    sort(ElemAttr0, ElemAttr1), sort_1(ElemAttr1, ElemAttr),
    mrb_is_vector_element(ElemAttr, Attr, no, yes), !.
mrb_is_vector_element([car('$VAR'(N))|Vattr], Attr, _, yes) :-
    aref(Attr, N, ElemAttr0),
    sort(ElemAttr0, ElemAttr1), sort_1(ElemAttr1, ElemAttr),
    mrb_is_vector_element(ElemAttr, Attr, no, yes), !.
mrb_is_vector_element([cdr('$VAR'(N))|Vattr], Attr, _, yes) :-
    aref(Attr, N, ElemAttr0),
    sort(ElemAttr0, ElemAttr1), sort_1(ElemAttr1, ElemAttr),
    mrb_is_vector_element(ElemAttr, Attr, no, yes), !.
mrb_is_vector_element([_|Vattr], Attr, Flag0, Flag) :- !,
    mrb_is_vector_element(Vattr, Attr, Flag0, Flag).

:- mode mrb_update_To_table_of_gc_code(+, +, +, -).
mrb_update_To_table_of_gc_code([], _, To, To) :- !.
mrb_update_To_table_of_gc_code([Gc_code|Cdr], CommitPC, To0, To) :- 
    functor(Gc_code, _, A),
    mrb_update_To_table(A, Gc_code, CommitPC, To0, To1),
    mrb_update_To_table_of_gc_code(Cdr, CommitPC, To1, To).

:- mode mrb_update_To_table(+, +, +, +, -).
mrb_update_To_table(0, _, _, To, To) :- !.
mrb_update_To_table(A, Code, CommitPC, To0, To2) :-
    arg(A, Code, '$VAR'(N)), !,
    ( aref(To0, N, End), End < CommitPC, !, 
	aset(To0, N, CommitPC, To1) ;
      To1 = To0 ),
    A1 is A-1,
    mrb_update_To_table(A1, Code, CommitPC, To1, To2).
mrb_update_To_table(A, Code, CommitPC, To0, To1) :-
    A1 is A-1,
    mrb_update_To_table(A1, Code, CommitPC, To0, To1).


%%%%% MRB OPTIMIZATION OF BODY PART

:- mode mrb_body(+, -, ?, +, +).
mrb_body([], Code, Code, _, Bref-Bref) :- !.
mrb_body([Inst|Body], [NewInst|Code0], Code1, Gref, Bref0-Bref2) :- 
    mrb_one_body_code(Inst, NewInst, Gref, Bref0-Bref1), !,
    mrb_body(Body, Code0, Code1, Gref, Bref1-Bref2).
mrb_body([Inst|Body], [Inst|Code0], Code1, Gref, BREFS) :- 
    mrb_body(Body, Code0, Code1, Gref, BREFS).

:- mode mrb_one_body_code(+, -, +, +).
mrb_one_body_code(get_value(Ai,Aj), NewInst, Gref, BREFs) :- !,
    mrb_mark_check_of_get_value(Ai, Aj, NewInst, Gref, BREFs).
mrb_one_body_code(put_variable(Aj,Ai),
                  put_marked_variable(Aj,Ai), Gref, Bref0-Bref1) :-
  ( mrb_variable_mark_check(Aj, Bref0), !,
	mrb_set_marked_sign_to_Bref(Bref0, Aj, Bref1) ;
    mrb_variable_mark_check(Ai, Bref0),
	mrb_set_marked_sign_to_Bref(Bref0, Ai, Bref1) ).
mrb_one_body_code(Inst, NewInst, Gref, Bref0-Bref1) :- 
    mrb_is_mark_variable_check_inst(Inst, NewInst, A),
    mrb_variable_mark_check(A, Bref0), !,
    mrb_set_marked_sign_to_Bref(Bref0, A, Bref1).
mrb_one_body_code(Inst, NewInst, Gref, Bref0-Bref1) :- 
    mrb_is_mark_value_check_inst(Inst, NewInst, A),
    mrb_value_mark_check(A, Gref, Bref0), !,
    mrb_set_marked_sign_to_Bref(Bref0, A, Bref1).
%mrb_one_body_code(Inst, Inst, Gref, Bref-Bref) :- !.

:- mode mrb_mark_check_of_get_value(+, +, -, +, +).
mrb_mark_check_of_get_value(Ai, Aj, 
                  get_both_marked_value(Ai,Aj), Gref, Bref0-Bref2) :- 
    mrb_value_mark_check(Ai, Gref, Bref0),
    mrb_value_mark_check(Aj, Gref, Bref0), !,
    mrb_set_marked_sign_to_Bref(Bref0, Ai, Bref1),
    mrb_set_marked_sign_to_Bref(Bref1, Aj, Bref2).
mrb_mark_check_of_get_value(Ai, Aj, 
                  get_marked_value(Ai,Aj), Gref, Bref0-Bref1) :-
    mrb_value_mark_check(Ai, Gref, Bref0), !,
    mrb_set_marked_sign_to_Bref(Bref0, Ai, Bref1).
mrb_mark_check_of_get_value(Ai, Aj, 
                  get_marked_value(Aj,Ai), Gref, Bref0-Bref1) :-
    mrb_value_mark_check(Aj, Gref, Bref0), !,
    mrb_set_marked_sign_to_Bref(Bref0, Aj, Bref1).
mrb_mark_check_of_get_value(Ai, Aj, get_value(Aj,Ai), _, Bref-Bref) :- !.

:- mode mrb_is_mark_variable_check_inst(+, -, -).
mrb_is_mark_variable_check_inst(set_variable(Aj,Gi), 
                                set_marked_variable(Aj,Gi), Aj) :- !.
mrb_is_mark_variable_check_inst(write_car_variable(Al,Ai),
                                write_car_marked_variable(Al,Ai), Ai) :- !.
mrb_is_mark_variable_check_inst(write_cdr_variable(Al,Ai),
                                write_cdr_marked_variable(Al,Ai), Ai) :- !.
mrb_is_mark_variable_check_inst(write_element_variable(Al,I,Ai),
                                write_element_marked_variable(Al,I,Ai), 
				Ai) :- !.

:- mode mrb_is_mark_value_check_inst(+, -, -).
mrb_is_mark_value_check_inst(set_value(Aj,Gi),
                             set_marked_value(Aj,Gi), Aj) :- !.
mrb_is_mark_value_check_inst(put_value(Aj,Ai),
                             put_marked_value(Aj,Ai), Aj) :- !.
mrb_is_mark_value_check_inst(get_constant(C,Ai),
                             get_marked_constant(C,Ai), Ai) :- !.
mrb_is_mark_value_check_inst(get_list_value(Aj,Ai),
                             get_list_marked_value(Aj,Ai), Ai) :- !.
mrb_is_mark_value_check_inst(get_vector_value(Aj,Ai),
                             get_vector_marked_value(Aj,Ai), Ai) :- !.
mrb_is_mark_value_check_inst(write_car_value(Al,Ai),
          	             write_car_marked_value(Al,Ai), Ai) :- !.
mrb_is_mark_value_check_inst(write_cdr_value(Al,Ai),
          	             write_cdr_marked_value(Al,Ai), Ai) :- !.
mrb_is_mark_value_check_inst(write_element_value(Av,I,Ai),
          	             write_element_marked_value(Av,I,Ai), 
			     Ai) :- !.

:- mode mrb_value_mark_check(+, +, +).
mrb_value_mark_check('$VAR'(N), Gref, Bref) :-
    aref(Gref, N, P), aref(Bref, N, B), 
    ( P > 0, B >= 2, ! ; P =:= 0, B >= 3 ).

:- mode mrb_variable_mark_check(+, +).
mrb_variable_mark_check('$VAR'(N), Bref) :-
    aref(Bref, N, B), B >= 3, !.

:- mode mrb_set_marked_sign_to_Bref(+, +, -).
mrb_set_marked_sign_to_Bref(Bref0, '$VAR'(N), Bref1) :-
    aset(Bref0, N, -1, Bref1).		% -1 means marked.	       


%%%%% Reuse structure option 

:- mode mrb_get_reusable_structure_reg(+, -, ?).
mrb_get_reusable_structure_reg([], ReuseReg, ReuseReg) :- !.
mrb_get_reusable_structure_reg([collect_list(V)|Gc_code], 
	                       [list(V,PC)|ReuseReg0], ReuseReg1) :- !,
    mrb_get_reusable_structure_reg(Gc_code, ReuseReg0, ReuseReg1).
mrb_get_reusable_structure_reg([collect_vector(V,N)|Gc_code], 
	                       [vector(N,V,PC)|ReuseReg0], ReuseReg1) :- !,
    mrb_get_reusable_structure_reg(Gc_code, ReuseReg0, ReuseReg1).
mrb_get_reusable_structure_reg([_|Gc_code], ReuseReg0, ReuseReg1) :- !,
    mrb_get_reusable_structure_reg(Gc_code, ReuseReg0, ReuseReg1).

:- mode mrb_body_with_reuse_option(+, -, ?, +, +, +, +, +).
mrb_body_with_reuse_option([], Code, Code, _, 
	                   _, UsedReg-UsedReg, _, Bref-Bref) :- !.
mrb_body_with_reuse_option([Inst|Body0], [NewInst|New0], New1, PC0, 
			   ReuseReg, USEDREG, Gref, Bref0-Bref2) :- 
    mrb_one_body_code(Inst, NewInst, Gref, Bref0-Bref1), !,
    PC1 is PC0 + 1,
    mrb_body_with_reuse_option(Body0, New0, New1, PC1, 
			       ReuseReg, USEDREG, Gref, Bref1-Bref2).
mrb_body_with_reuse_option([Inst|Body0], [NewInst|New0], New1, PC0, 
			   ReuseReg0, UsedReg0-UsedReg2, Gref, BREFS) :-
    mrb_one_reuse_option(Inst, NewInst, PC0, 
	                 ReuseReg0, ReuseReg1, UsedReg0-UsedReg1), !, 
    PC1 is PC0 + 1,
    mrb_body_with_reuse_option(Body0, New0, New1, PC1, ReuseReg1, 
	                       UsedReg1-UsedReg2, Gref, BREFS).
mrb_body_with_reuse_option([Inst|Body0], [Inst|New0], New1, PC0, 
			   ReuseReg, USEDREG, Gref, BREFS) :-
    PC1 is PC0 + 1,
    mrb_body_with_reuse_option(Body0, New0, New1, PC1, 
			       ReuseReg, USEDREG, Gref, BREFS).

:- mode mrb_one_reuse_option(+, -, +, +, -, +). 
mrb_one_reuse_option(put_list(Ai), 
	             put_reused_list(Xj,Ai), 
		     PC0, 
		     ReuseReg0, ReuseReg1, 
		     [(Xj,PC0)|UsedReg]-UsedReg) :- 
    mrb_check_structure_reusable(ReuseReg0, list(Xj,PC0), ReuseReg1), !.
mrb_one_reuse_option(set_list(Gi), 
	             set_reused_list(Xj,Gi), 
		     PC0, 
		     ReuseReg0, ReuseReg1,
		     [(Xj,PC0)|UsedReg]-UsedReg) :- 
    mrb_check_structure_reusable(ReuseReg0, list(Xj,PC0), ReuseReg1), !.
mrb_one_reuse_option(put_vector(Ai,N), 
	             put_reused_vector(Xj,Ai,N), 
		     PC0, 
		     ReuseReg0, ReuseReg1,
		     [(Xj,PC0)|UsedReg]-UsedReg) :- 
    mrb_check_structure_reusable(ReuseReg0, vector(N,Xj,PC0), ReuseReg1), !.
mrb_one_reuse_option(set_vector(Gi,N), 
	             set_reused_vector(Xj,Gi,N), 
		     PC0, 
		     ReuseReg0, ReuseReg1,
		     [(Xj,PC0)|UsedReg]-UsedReg) :- 
    mrb_check_structure_reusable(ReuseReg0, vector(N,Xj,PC0), ReuseReg1), !.

:- mode mrb_check_structure_reusable(+, +, -).
mrb_check_structure_reusable([], _, []) :- !, fail.
mrb_check_structure_reusable([One|ReuseReg], Key, ReuseReg) :-
    mrb_check_reuse_reg(One, Key), !.
mrb_check_structure_reusable([One|ReuseReg], Key, [One|Tail]) :- !,
    mrb_check_structure_reusable(ReuseReg, Key, Tail).

:- mode mrb_check_reuse_reg(+, +).
mrb_check_reuse_reg(list(V,PC), list(V,PC)) :- !.
mrb_check_reuse_reg(vector(N,V,PC), vector(N,V,PC)) :- !.

:- mode mrb_update_gc_code(+, +, -, ?).
mrb_update_gc_code([], _, New, New) :- !.
mrb_update_gc_code([collect_list(V)|Gc_code], UsedReg0, New0, New1) :-
    mrb_drop_one_reuse_code(UsedReg0, V, UsedReg1), !,
    mrb_update_gc_code(Gc_code, UsedReg1, New0, New1).
mrb_update_gc_code([collect_vector(V,_)|Gc_code], UsedReg0, New0, New1) :-
    mrb_drop_one_reuse_code(UsedReg0, V, UsedReg1), !,
    mrb_update_gc_code(Gc_code, UsedReg1, New0, New1).
mrb_update_gc_code([One|Gc_code], UsedReg0, [One|New0], New1) :-
    mrb_update_gc_code(Gc_code, UsedReg0, New0, New1).

:- mode mrb_drop_one_reuse_code(+, +, -).
mrb_drop_one_reuse_code([(V,_)|UsedReg], V, UsedReg) :- !.
mrb_drop_one_reuse_code([One|UsedReg], V, [One|Tail]) :- !,
    mrb_drop_one_reuse_code(UsedReg, V, Tail).

:- mode mrb_update_To_table_of_reused_reg(+, +, -).
mrb_update_To_table_of_reused_reg([('$VAR'(N), PC)|UsedReg], To0, To2) :- !,
    aset(To0, N, PC, To1),
    mrb_update_To_table_of_reused_reg(UsedReg, To1, To2).
mrb_update_To_table_of_reused_reg([], To, To) :- !.

