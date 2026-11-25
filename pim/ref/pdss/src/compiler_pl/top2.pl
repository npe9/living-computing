%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% <YKIMURA>KL1CMP.PL.32,  9-Nov-87 19:07:58, Edit by YKIMURA
% <CHIKAYAMA.CP>FGHCMP.PL.53,  7-Aug-86 16:55:47, Edit by CHIKAYAMA

%%% KL1 Compiler %%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     Ver. 0.5  87.05.08     %
%   first author CHIKAYAMA   %
%   modified     YKIMURA     %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Implemented 'otherwise' by D.Sekita 870902
% Implemented 'alternatively' by D.Sekita 870903
% Optimized for SICSTUS Prolog by T.Chikayama 871130

:- op(1150,  fx, (with_macro)).		% Use for user macro reference.
:- op(1150,  fx, (user_macro)).		% Use for user macro library name.
:- op(1150,  fx, (implicit)).		% Use for implicit argument
:- op(1150,  fx, (local_implicit)).	% Use for implicit argument
:- op(1090, xfx, (=>)).			% Use for user macro definition.
:- op( 800, xfx, (:)).			% External Call
:- op( 700, xfx, (:=)).			% Becomes
:- op( 700, xfx, (<=)).			% Implicit Argument
:- op( 700, xfx, (<<=)).		% Implicit Argument
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
/* for Floating Point Expression */  % 890404 Nishizaki
:- op( 700, xfx, ($:=)).		% Becomes
:- op( 700, xfx, ($<=)).		% Implicit Argument
:- op( 700, xfx, ($=:=)).		% Equal
:- op( 700, xfx, ($=\=)).		% Not Equal
:- op( 700, xfx, ($<)).			% Less Than
:- op( 700, xfx, ($>=)).		% Not Less Than
:- op( 700, xfx, ($>)).			% Greater Than
:- op( 700, xfx, ($=<)).		% Not Greater Than
:- op( 300, xfy, (**)).			% Power

:- public kl1compile/0, ghccompile/1, tsscomp/2, tsscomp/0, gotss/0,
	  klb_version/1, put_string/1, go/0, go_sics/0, test_reader/0.

%%%% to generate exec file on DEC-10 PROLOG

go :- plsys(core_image), !, nolog, kl1compile, halt.

gotss :- plsys(core_image), !, nolog, tsscomp, halt.

%%%% to generate save image file on SICStus PROLOG

go_sics :- save(kl1cmp), !, kl1compile, halt.

go_index :- save(kl1index), !, kl1compile, halt.

:- mode klb_version(-).
klb_version('**** KL1/B Compiler Ver.0.96(890922) ****'). 

kl1compile_for_pimos :- 
    recorda('$$$new_unique_number_for_case_expansion', 0, _), 
    klb_version(Version), ttynl, display(Version), ttynl, ttynl,
    display('Compiler Mode : '), read(Mode),
    display('Indexing    : '), read(Index),
    display('Gc option   : '), read(Gc),
    display('Input  file : '), read(S),
    assert(('$$$user_macro_definition_list'([]))),
    update_usable_builtin_predicate_level(Mode),
    kl1_compile_files(S, Index-Gc).

:- mode kl1_compile_files(+, +).
kl1_compile_files('end_of_file', _) :- !.
kl1_compile_files(S, Flag) :- 
    display('Output file : '), read(O),
    see(S), tell(O),
    ghccompile(Flag), 
    seen, told,
    format('~w is compiled', [S]), ttynl, fail.
kl1_compile_files(_, Flag) :- 
    display('Input  file : '), read(S),
    kl1_compile_files(S, Flag).

kl1compile :- 
    recorda('$$$new_unique_number_for_case_expansion', 0, _), 
    klb_version(Version), ttynl, display(Version), ttynl, ttynl,
    display('Compiler Mode : '), read(Mode),
    display('Indexing    : '), read(Index),
    display('Gc option   : '), read(Gc),
    display('Input  file : '), read(S),
    display('Output file : '), read(O),
    assert(('$$$user_macro_definition_list'([]))),
    update_usable_builtin_predicate_level(Mode),
    see(S), tell(O),
    ghccompile(Index-Gc), 
    seen, told,
    format('~w is compiled', [S]), ttynl.

:- mode ghccompile(+).
ghccompile(Flags) :-
    abolish((=>)/2),
    assert(((Pat=>Pat) :- fail)),
    read(Directive),
    read_directives(Directive, Module, Ext-[], []-It, Clause),
    output_module_information(Module, Ext),
    read_clause(Clause, Clause1, Flags, []-Ex),
    read_and_compile_predicate(Clause1, Flags, It, Ex-Ex1),
    compile_extra_clauses(Ex1, Flags),
    display('END'), ttynl, !.

:- mode tsscomp(+, +).
tsscomp(Index, Opt) :-				% 86,8,9 YKIMURA	
    recorda( '$$$new_unique_number_for_case_expansion', 0, _), 
    prompt(Old, '-> '),			
    cl_read(Clause, Flags, []-Ex),
    read_and_compile_predicate(Clause, Flags, [], Ex-Ex1),
    compile_extra_clauses(Ex1, Flags).

tsscomp :- 
    recorda( '$$$new_unique_number_for_case_expansion', 0, _), 
    display('Indexing  : '), read(Index),
    display('Gc option : '), read(Gc),
    prompt(Old, '-> '), cl_read(Clause, Index-Gc, []-Ex),
    ( Clause \== end_of_file, !, 
         read_and_compile_predicate(Clause, Index-Gc, [], Ex-Ex1),
	 compile_extra_clauses(Ex1, Index-Gc),
      display( 'END' ), true ).

compile_extra_clauses([], _).
compile_extra_clauses([(M:F/A,ExP)|Ex], Flag) :-
	new_external_clause(ExP,M,F,A,ExC),
	( compile_by_option(ExP/A, ExC, [[1]], Flag, []), fail;
%	  display(ExP/A), display(','), ttyflush ), !,
	  display(ExP),display('/'),display(A), display(','), ttyflush ), !,
	compile_extra_clauses(Ex, Flag).
compile_extra_clauses([(F/A@Pragma,ExP,_)|Ex], Flag) :-
	new_pragma_clause(ExP,Pragma,F,A,Ar,ExC),
	( compile_by_option(ExP/Ar, ExC, [[1]], Flag, []), fail;
%	  display(ExP/Ar), display(','), ttyflush ), !,
	  display(ExP),display('/'),display(Ar), display(','), ttyflush ), !,
	compile_extra_clauses(Ex, Flag).

new_external_clause(ExP,M,F,A,ExC) :-
    new_clause_args(A,HArgs,BArgs),
    H =.. [ExP|HArgs],
    P =.. [F|BArgs],
    ExC = [[(H :- true | M:P)]].

new_pragma_clause(ExP,Pragma,F,A,Ar,ExC) :-
    new_clause_args(A,HArgs,BArgs),
    functor(Pragma,_,PA), Ar is A + PA,
    Pragma =.. [_|PArgs],
    append(HArgs,PArgs,HPArgs),
    H =.. [ExP|HPArgs],
    P =.. [F|BArgs],
    ExC = [[(H :- true | P@Pragma)]].

new_pragma_variable([_|A],[One|P],N,PA) :-
    N1 is N + 1, new_pragma_variable(A,P,N1,PA).
new_pragma_variable([],[],N,N).

new_clause_args(0,[],[]) :- !.
new_clause_args(A,HArgs,BArgs) :- !,
    HArgs = [Arg|HArgsL], BArgs = [Arg|BArgsL],
    A1 is A - 1,
    new_clause_args(A1,HArgsL,BArgsL).

:- mode read_directives(+, ?, +, +, -).	
read_directives((:- op(Prec,Type,Op)), Module, EXT, IT, Clause) :- !,
    call(op(Prec, Type, Op)),
    read(Next),
    read_directives(Next, Module, EXT, IT, Clause).
read_directives((:- public D), Module, Ext0-Ext2, It0-It1, Clause) :- !,
    convert_public_declaration(D, Ext0, Ext1),
    read(Next),
    read_directives(Next, Module, Ext1-Ext2, It0-It1, Clause).
read_directives((:- with_macro Mac), Module, EXT, IT, Clause) :- !,
    read_user_macro_definition(Mac),    % --> macro.pl
    read(Next),
    read_directives(Next, Module, EXT, IT, Clause).
read_directives((:- implicit Args), Module, EXT, IT, Clause) :- !,
    check_declaration_of_implicit_args(Args, Ha, Ta),
    replace_implicit_arg_template(global_implicit_args, Ha, Ta),
    read(Next),
    read_directives(Next, Module, EXT, IT, Clause).
read_directives((:- local_implicit Args), Module, EXT, IT, Clause) :- !,
    check_declaration_of_implicit_args(Args, Ha, Ta),
    replace_implicit_arg_template(local_implicit_args, Ha, Ta),
    read(Next),
    read_directives(Next, Module, EXT, IT, Clause).
read_directives((:- local_implicit), Module, EXT, IT, Clause) :- !,
    replace_implicit_arg_template(local_implicit_args, Ha, Ha),
    read(Next),
    read_directives(Next, Module, EXT, IT, Clause).
read_directives((:- module D), D, Ext0-Ext1, It0-It1, Clause) :- !,
    read(Next),
    read_directives(Next, D, Ext0-Ext1, It0-It1, Clause).
read_directives((:- module D), Module, Ext0-Ext1, It0-It1, Clause) :- !,
    warn('module name is duplicated... ~w  - ignored', [D]),
    read(Next),
    read_directives(Next, Module, Ext0-Ext1, It0-It1, Clause).
read_directives((:- kl1_index(A)), Module, Ext0-Ext1, It0-It2, Clause) :- !,
    intern_index_pred(A, 1, It0, It1),
    read(Next),
    read_directives(Next, Module, Ext0-Ext1, It1-It2, Clause).
read_directives((:- kl1_noindex(A)), Module, Ext0-Ext1, It0-It2, Clause) :- !,
    intern_index_pred(A, 0, It0, It1),
    read(Next),
    read_directives(Next, Module, Ext0-Ext1, It1-It2, Clause).
read_directives((:- A), Module, Ext0-Ext1, It0-It1, Clause) :- !,
    warn('This declaration is ignored~n~w', [(:- A )]),
    read(Next),
    read_directives(Next, Module, Ext0-Ext1, It0-It1, Clause).
read_directives(Clause, _, Ext-Ext, It-It, Clause).

:- mode convert_public_declaration(+, -, ?).
convert_public_declaration((Car,Cdr), Ext0, Ext2) :- !,
    convert_public_declaration(Car, Ext0, Ext1),
    convert_public_declaration(Cdr, Ext1, Ext2).
convert_public_declaration(One, [One|Ext], Ext) :- !.


%%%%% COMPILER BODY MAIN ROUTINE

:- mode read_and_compile_predicate(+, +, +, +).
read_and_compile_predicate(end_of_file, _, _, Ex-Ex) :- !.
read_and_compile_predicate(First, Flags, It, Ex-Ex1) :- 
  ( First = otherwise, !; First = alternatively ), !,
    error('otherwise or alternatively found irregulary', []),
    cl_read(Next, Flags, Ex-Ex0),
    read_and_compile_predicate(Next, Flags, It, Ex-Ex1).
read_and_compile_predicate(First, Flags, It0, Ex-Ex1) :- !,
    identify_predicate(First, Pred),
    check_overlapped_builtin(Pred),
    read_predicate(First, Clauses, CnL, First_of_next, Flags-Pred,
							It0-It1, Ex-Ex0),
  ( compile_by_option(Pred, Clauses, CnL, Flags, It1), fail;
%    display(Pred), display(','), ttyflush ), !,
    Pred=F/A, display(F),display('/'),display(A), display(','), ttyflush ), !,
    read_and_compile_predicate(First_of_next, Flags, It1, Ex0-Ex1).

:- mode read_predicate(+, -, -, -, +, +, +).
read_predicate(Cls, [Clses|Rest], CnL, First_of_next, Flags-Pred,
							It0-It2, Ex-Ex1) :- 
    read_predicate_one_block(Cls, Clses, First_of_next1, 0-Cn, Flags-Pred,
							It0-It1, Ex-Ex0),
    check_if_block_end(First_of_next1, Rest, First_of_next, CnL, Cn,
						It1-It2, Ex0-Ex1, Flags-Pred).

:- mode check_if_block_end(+, -, -, -, +, +, +, +).
check_if_block_end(otherwise, [otherwise|Rest], First_of_next,
                              [Cn,0|CnL], Cn, IT, Ex-Ex1, Flags-Pred) :-
    cl_read(Next, Flags, Ex-Ex0),
    read_predicate(Next, Rest, CnL, First_of_next, Flags-Pred, IT, Ex0-Ex1).
check_if_block_end(alternatively, [alternatively|Rest], First_of_next,
                                  [Cn,0|CnL], Cn, IT, Ex-Ex1, Flags-Pred) :-
    cl_read(Next, Flags, Ex-Ex0),
    read_predicate(Next, Rest, CnL, First_of_next, Flags-Pred, IT, Ex0-Ex1).
check_if_block_end(First_of_next, [], First_of_next, [Cn], Cn, It-It, Ex-Ex,_).

:- mode read_predicate_one_block(+, -, -, +, +, +, +).
read_predicate_one_block(Cls, [Cls|Rest], First_of_next, Cn0-Cn, 
         				  Flags-Pred, IT, Ex-Ex1) :-
    identify_predicate(Cls, Pred), !,
    Cn1 is Cn0+1,
    cl_read(Next, Flags, Ex-Ex0),
    read_predicate_one_block(Next, Rest, First_of_next, Cn1-Cn, 
                                         Flags-Pred, IT, Ex0-Ex1).
read_predicate_one_block((:- Dir), [], First_of_next, CNs,
						Flags-Pred, IT, EX) :- !,
    check_if_inner_directive(Dir, First_of_next, CNs, Flags, IT, EX).
read_predicate_one_block(First_of_next, [], First_of_next, Cn-Cn, _,
						It-It, Ex-Ex).

:- mode check_if_inner_directive(+, -, +, +, +, +).
check_if_inner_directive(kl1_index(A), Next, Cn-Cn, Flags, It0-It1, EX) :- !,
    intern_index_pred(A, 1, It0, It1),
    cl_read(Next, Flags, EX).
check_if_inner_directive(kl1_noindex(A), Next, Cn-Cn, Flags, It0-It1, EX) :- !,
    intern_index_pred(A, 0, It0, It1),
    cl_read(Next, Flags, EX).
check_if_inner_directive(Dir, Next, Cn-Cn, Flags, It-It, EX) :-
    can_be_ignored_directive(Dir), !,
    cl_read(Next, Flags, EX).
check_if_inner_directive(Dir, Next, Cn-Cn, Flags, It-It, EX) :- !,
    warn('This declaration is ignored~n~w', [(:- Dir)]),
    cl_read(Next, Flags, EX).

:- mode can_be_ignored_directive(+).
can_be_ignored_directive((local_implicit)) :- !.
can_be_ignored_directive(local_implicit(_)) :- !.
can_be_ignored_directive(op(_,_,_)) :- !.

:- mode identify_predicate(+, ?).
identify_predicate((H:-G|B), F/A) :- !, functor(H, F, A).
identify_predicate((H:-B), F/A) :- !, functor(H, F, A).
identify_predicate(H, F/A) :- functor(H, F, A).

%%%%% CASE DISPATCH ON INDEXING OR NO INDEXING

:- mode compile_by_option(+, +, +, +, +).
compile_by_option(Pred, Clauses, CnL, Flags, It) :-
    output_code_header(Pred),
    output_label(Pred),
    compile_with_index(Clauses, Pred, 0-Label, CnL, Flags, It), !.

:- mode compile_with_index(+, +, +, +, +, +).
compile_with_index([], Pred, L-L, _, _, _) :- !, output_code_end(Pred).
compile_with_index([One_block|Rest], Pred, L0-L2, [Cn|CnL], Flags, It) :-
    compile_one_block(One_block, Pred, L0-L1, Cn, Flags, It), !,
    compile_with_index(Rest, Pred, L1-L2, CnL, Flags, It).

:- mode compile_one_block(+, +, +, +, +, +).
compile_one_block(One_block, Pred, L0-L0, Cn, _, _) :-
    is_break_instruction(One_block, Break_inst), !, 
    Break =.. [Break_inst, Pred],
    output_term_nl(Break).
compile_one_block(One_block, Pred, LABEL, Cn, Index-Gc, It) :-
    to_be_compiled_with_index(Index, Pred, Cn, It), !, 
    compile_block_with_index(One_block, Pred, Gc, Fail, Code, 
                                                        [label(Fail)]),
    optimize_kl1_code(Index, Code, Pred, LABEL).
compile_one_block(One_block, Pred, LABEL, Cn, Index-Gc, It) :-
    compile_predicate(One_block, Pred, LABEL, Gc).

:- mode is_break_instruction(+, -).
is_break_instruction(otherwise, otherwise) :- !.
is_break_instruction(alternatively, read_eagerly) :- !.

%%%%% COMPILATION WITH CLAUSE INDEXING

:- mode compile_block_with_index(+, +, +, ?, -, ?).
%compile_block_with_index(Clauses0, F/A, Gc, Fail, Code, Code) :-
%    error('Currently compilation with clause indexing is not allowed', []).
compile_block_with_index(Clauses0, F/A, Gc, Fail, Code0, Code1) :-
    predicate_dependency(Clauses0, Clauses1, [], 1), 
    make_index_arg_list(1, A, Arg_list, []),
    Reg is A+1,
    make_indexed_tree(Clauses1, Arg_list, Reg, Type_tree),
    compile_indexed_tree(Type_tree, (F/A,Gc), Fail, Code0, Code1).

:- mode compile_leaf_clause(+, +, ?, -, ?).
compile_leaf_clause(Gc, ClsTbl, Fail, CodeBegin, CodeEnd) :- 
    get_clause_variable_no(ClsTbl, Nv0),
    get_original_clause(ClsTbl, Cls),
%    write('% Indexed clause before compile_leaf_clause'), nl, % debug
%    write('      '), write(Cls), nl,                          % debug
    compile_one_clause(Cls, Nv0-Nv, Fail, PC,
		       From0-To0-Reg0, Gref0-Bref0,
		       Type0-Attr0,
		       Code0, []),
  %  write('% After compile_one_clause '), nl,    % debug ykimura
  %  write_original_code(Code0, 0), nl,		% !!!
  %  write('% After compile_one_clause(F-T-R)'), nl,    % debug ykimura
  %  dump_tables(Nv, From0-To0-Reg0),		% !!!
  %  write('% After compile_one_clause(Argtbl)'), nl,    % debug ykimura
  %  dump_argtbl(Nv, Argtbl),			% !!!
    gc_option(Gc, Code0, Code, Type0-Attr0, From0-To0-Gref0-Bref0, 
                                            From-To-Gref-Bref),
  %  write('% After mrb_optimization'), nl,      % debug ykimura
  %  write_original_code(Code, 0), nl,		% !!!
  %  dump_tables(Nv, From-To-Reg0),		% !!!
    array(PC, Used0, 0),
  %  write('% Before register_predefined(Used)'), nl,	% debug
  %  dump_array(PC, Used0),			% debug
    register_predefined(Nv, From, To, Reg0, Used0, Used1),
  %  write('% Before register_preference(Used)'), nl,	% debug
  %  display('% Before register_preference'), ttynl,	% debug
  %  print_execute_time(G1, G2),			% statistics
  %  dump_array(PC, Used1),			% debug
    register_preference(Code, From-To-Reg0, From1-To1-Reg1, Used1, Used2),
  %  write('% After register_preference(Used)'), nl,	% debug
  %  dump_array(PC, Used2),			% debug
    determine_registers(0, Nv, From1, To1, Reg1, Used2, Reg, Used),
  %  write('% After determine_registers(Used)'), nl,	% debug
  %  dump_array(PC, Used),			% !!!
  %  write('% After determine registers(F-T-R)'), nl,	% debug ykimura
  %  dump_tables(Nv, From1-To1-Reg),		% !!!
  %  write('% Original code'), nl,		% debug
  %  write_original_code(Code, 0), nl,		% debug
    update_object_code(Code, From1-To1-Reg, 0, CodeBegin, CodeEnd).

%%%%% COMPILATION WITHOUT CLAUSE INDEXING

:- mode compile_predicate(+, +, +, +).
compile_predicate([One|Rest], Pred, L0-L1, Gc) :-
    L1 is L0+1,
    compile_one(One, Pred, L1, Gc),
    output_label(Pred/L1),
    fail.
compile_predicate([One|Rest], Pred, L0-L2, Gc) :-
    L1 is L0+1,
    compile_predicate(Rest, Pred, L1-L2, Gc).
compile_predicate([], Pred, L0-L1, _) :- !,
    L1 is L0+1.

:- mode compile_one(+, +, +, +).
compile_one(One, Pred, C, Gc) :-
    compile_one_predicate(One, Pred, C, Gc), !.
compile_one(One, Pred, C, _) :-
    error('Failed to compile a clause ~w of ~w:~n~q', [C, Pred, One]),
    fail.

:- mode compile_one_predicate(+, +, +, +).
compile_one_predicate(One, Pred, C0, Gc) :- 
    convert_one_clause(One, NewOne, 0, Nv0),
    compile_one_clause(NewOne, Nv0-Nv, Pred/C0, PC,     % numbering order is
		       From0-To0-Reg0, Gref0-Bref0,     % essential
		       Type0-Attr0,
		       Code0, []),
    gc_option(Gc, Code0, Code, Type0-Attr0, From0-To0-Gref0-Bref0, 
	                                    From-To-Gref-Bref),
    array(PC, Used0, 0),
    register_predefined(Nv, From, To, Reg0, Used0, Used1),
    register_preference(Code, From-To-Reg0, From1-To1-Reg1, Used1, Used2),
    determine_registers(0, Nv, From1, To1, Reg1, Used2, Reg, Used),
    update_object_code(Code, From1-To1-Reg, 0, Outcode, []),
    output_noindexed_code(Outcode).

:- mode compile_one_clause(+, +, ?, -, +, +, +, -, ?).
compile_one_clause(Clause, Nv0-Nv, Fail, PC, From-To-Reg, 
                                             Gref-Bref,
					     Aux1) -->
    { normalize(Clause, H, G, B, Nv0-Nv),
    %  write('% After number_vars '), nl,	% debug ykimura
    %  write('% Nv    is '), write(Nv), nl,	% debug ykimura
    %  write('% Guard is '), nl,			% debug ykimura
    %  write_original_code(G, 0), nl,	        % debug ykimura
    %  write('% Body  is '), nl,			% debug ykimura	      
    %  write_original_code(B, 0), nl,		% debug ykimura
      array(Nv, From0, []),
      array(Nv, To0, []),
      array(Nv, Reg0, []),
      array(Nv, Gref0, 0),
      array(Nv, Bref0, 0),
      array(Nv, Type0, []),
      array(Nv, Attr0, []),
      functor(H, _, A),
      initiate_head_arguments(A, H, From0-To0-Gref0, Tabs1, Reg0, Reg1) },
    %{ write('% Before compile_guard '), nl,		% debug ykimura
    %  dump_tables(Tabs1) },				% debug ykimura
    compile_guard([try_me_else(Fail)|G], Fail, 0, PC1, Tabs1-Tabs2, 
                                                       (Type0-Attr0)-Aux1,
						       1-Keep),
    % { write('% PC_comitted = '), write(Keep), nl },	% debug
    { keep_head_arguments(A, H, Keep, Tabs2, From1-To1-Gref) },
    compile_body([commit|B], PC1, PC, 
			     From1-To1-Bref0, 
			     From-To-Bref,
			     Reg1-Reg).

:- mode initiate_head_arguments(+, +, +, -, +, -).
initiate_head_arguments(0, _, Tabs, Tabs, Reg, Reg) :- !.
initiate_head_arguments(K, X, Tabs0, Tabs, Reg0, Reg) :-
    arg(K, X, A),
    newvar(A, 0, Tabs0, Tabs1),
    usereg(A, K, Reg0, Reg1),
    K1 is K-1,
    initiate_head_arguments(K1, X, Tabs1, Tabs, Reg1, Reg).

:- mode keep_head_arguments(+, +, +, +, -).
keep_head_arguments(K, X, T, From-To0-Gref, From-To-Gref) :-
    keep_head_args(K, X, T, To0, To).

:- mode keep_head_args(+, +, +, +, -).
keep_head_args(0, _, _, To, To) :- !.
keep_head_args(K, X, T, To0, To) :-
    arg(K, X, A),
  ( ref_To_table(A, To0, Res), Res < T, !,			% bug001
	set_To_table(A, T, To0, To1) ;
    To1 = To0 ),
    K1 is K-1,
    keep_head_args(K1, X, T, To1, To).

:- mode check_overlapped_builtin(+).
check_overlapped_builtin(F/A):-
    body_blt(F, A, _, _, _, Comp_mode), 
    check_if_this_is_legal_builtin(Comp_mode), !,
    warn('~w overlapped with builtin predicate', [F/A]).
check_overlapped_builtin(merge/3):-
    warn('~w overlapped with builtin macro', [merge/3]).
check_overlapped_builtin(merge_in/3):-
    warn('~w overlapped with builtin macro', [merge_in/3]).
check_overlapped_builtin(_).
