%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% This file specifies various parameters of PDSS.

:- public macro_library_directory/1, number_of_registers/1, 
          number_of_argument_slots/1, 
	  usable_builtin_predicate_level/1, 
	  update_usable_builtin_predicate_level/1,
	  kl1compile_for_pdss/0,
	  make_kl1cmp_for_pdss/0.


pdss_version('****       for PDSS Ver.2.52(890922) ****').
make_kl1cmp_for_pdss :-
    compile('top2.pl'),
    compile('read.pl'),
    compile('write2.pl'),
    compile('norm3.pl'),
    compile('comp2.pl'),
    compile('mrb4.pl'),
    compile('reg.pl'),
    compile('index2.pl'),
    compile('macro2.pl'),
    compile('convert.pl'),
    compile('code_opt2.pl'),
    compile('aux2.pl'),
    compile('pdss_blt.pl'),
    compile('libdir.pl'),
    save(kl1cmp), !,
    kl1compile_for_pdss, halt.

kl1compile_for_pdss :- 
    recorda('$$$new_unique_number_for_case_expansion', 0, _), 
    klb_version(Version), display(Version), ttynl,
    pdss_version(V2), display(V2), ttynl, ttynl,
    display('Compiler Mode : '), read(Mode),
    ( Mode == end_of_file, !, error('end_of_file was read'), halt;
    display('Indexing      : '), read(Index),
    display('Gc option     : '), read(Gc),
    display('Input  file   : '), read(S),
    display('Output file   : '), read(O),
    assert(('$$$user_macro_definition_list'([]))),
    update_usable_builtin_predicate_level(Mode),
    see(S), tell(O),
    ghccompile(Index-Gc), 
    seen, told,
    format('~w is compiled', [S]), ttynl ).


% User defined macro routine definition.
%:- mode macro_library_directory(-).
%macro_library_directory("/login2/pdss/pdss2.0/lib/macro/").

% Specification of the number of argument registers
:- mode number_of_registers(-).
number_of_registers(32).

% Specification of the number of argument slots in goal records.
:- mode number_of_argument_slots(-).
number_of_argument_slots(32).

% Specification of the builtin predicates 
:- mode usable_builtin_predicate_level(-).
usable_builtin_predicate_level(1).                % 1 means 'user'.

:- mode update_usable_builtin_predicate_level(+).
update_usable_builtin_predicate_level(Flag) :-
    abolish(usable_builtin_predicate_level, 1),
    set_usable_builtin_predicate_level(Flag). 

:- mode set_usable_builtin_predicate_level(+).
set_usable_builtin_predicate_level(pdss) :- !,  
    assert((usable_builtin_predicate_level(3))).     % pdss = '0011'.
set_usable_builtin_predicate_level(user) :- !,
    assert((usable_builtin_predicate_level(1))).     % user = '0001'.
set_usable_builtin_predicate_level(Flag) :- !,
    error('Illegal specification: ~w', [Flag]),
    assert((usable_builtin_predicate_level(1))).     % user = '0001'.

:- mode check_if_this_is_legal_builtin(+).
check_if_this_is_legal_builtin(Flag) :- 
    get_flag_value(Flag, Value), 
    usable_builtin_predicate_level(Mode),
    Value /\ Mode =\= 0, !.

:- mode get_flag_value(+, -).
get_flag_value(pdss,  2) :- !.                     % pdss  = '0010'.
get_flag_value(user,  1) :- !.                     % user  = '0001'.

%%%%%%% Option for clause indexing
%% If the number of clauses read in is larger than this number,
%% these clauses are compiled with clause indexing option.

:- mode number_of_clauses_to_be_compiled_with_index(-).
number_of_clauses_to_be_compiled_with_index(0).
