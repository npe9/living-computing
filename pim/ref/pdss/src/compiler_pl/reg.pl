%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1992.					 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% REGISTER ALLOCATION

:- mode register_predefined(+, +, +, +, +, -).
register_predefined(0, _, _, _, Used, Used) :- !.
register_predefined(V, From, To, Reg, Used0, Used) :-
    V1 is V-1, aref(Reg, V1, R), integer(R), !,
    aref(From, V1, Fv), aref(To, V1, Tv),
    use_register(Fv, Tv, R, Used0, Used1),
    register_predefined(V1, From, To, Reg, Used1, Used).
register_predefined(V, From, To, Reg, Used0, Used) :-
    V1 is V-1,
    register_predefined(V1, From, To, Reg, Used0, Used).

:- mode register_preference(+, +, +, +, -).
register_preference([], From-To-Reg, From-To-Reg, Used, Used) :- !.
register_preference([Instr|Rest], From0-To0-Reg0, FromToReg, Used0, Used) :-
    preference(Instr, Reg0, X, Y, R),
    aref(From0, X, FX), aref(To0, X, TX),
    aref(From0, Y, FY), aref(To0, Y, TY),
    T0 = FY,
    return_less(FX, FY, F0),
    F1 = TY,
    return_greater(TY, TX, T1),
    register_available(F0, T0, R, Used0),
    register_available(F1, T1, R, Used0), !,
    use_register(F0, T0, R, Used0, Used1),
    use_register(F1, T1, R, Used1, Used2),
    aset(From0, X, F0, From1), aset(To0, X, T1, To1),
    aset(From1, Y, F0, From2), aset(To1, Y, T1, To2),
    aset(Reg0, X, R, Reg1), aset(Reg1, Y, R, Reg2),
    register_preference(Rest, From2-To2-Reg2, FromToReg, Used2, Used).
register_preference([Instr|Rest], From0-To0-Reg0, FromToReg, Used0, Used) :-
    preference_for_same_reg(Instr, Reg0, X, Y), !,	% both variable
    aref(From0, X, FX), aref(To0, X, TX), 
    aref(From0, Y, FY), aref(To0, Y, TY), 
    return_less(FX, FY, F), return_greater(TY, TX, T),
    number_of_registers(Max),
    find_free_register(R, F, T, Used0, Used1),
    aset(From0, X, F, From1), aset(To0, X, T, To1),
    aset(From1, Y, F, From2), aset(To1, Y, T, To2),
    aset(Reg0, X, R, Reg1), aset(Reg1, Y, R, Reg2),
    register_preference(Rest, From2-To2-Reg2, FromToReg, Used1, Used).
register_preference([_|Rest], From0To0Reg0, FromToReg, Used0, Used) :-
    register_preference(Rest, From0To0Reg0, FromToReg, Used0, Used).

:- mode return_less(+, +, -).
return_less(X, Y, X) :- X < Y, !.
return_less(X, Y, Y) :- !.

:- mode return_greater(+, +, -).
return_greater(X, Y, Y) :- X < Y, !.
return_greater(X, Y, X) :- !.

:- mode preference(+, +, -, -, -).
preference(void_variable('$VAR'(X),'$VAR'(Y)), Reg, X, Y, R) :-
    aref(Reg, Y, R), integer(R), aref(Reg, X, []), !.
preference(void_variable('$VAR'(Y),'$VAR'(X)), Reg, X, Y, R) :-
    aref(Reg, Y, R), integer(R), aref(Reg, X, []), !.
preference(wait_variable('$VAR'(X),'$VAR'(Y)), Reg, X, Y, R) :-
    aref(Reg, Y, R), integer(R), aref(Reg, X, []), !.
preference(wait_variable('$VAR'(Y),'$VAR'(X)), Reg, X, Y, R) :-
    aref(Reg, Y, R), integer(R), aref(Reg, X, []), !.
preference(put_value('$VAR'(X),'$VAR'(Y)), Reg, X, Y, R) :-
    aref(Reg, Y, R), integer(R), aref(Reg, X, []), !.
preference(put_value('$VAR'(Y),'$VAR'(X)), Reg, X, Y, R) :-
    aref(Reg, Y, R), integer(R), aref(Reg, X, []), !.

:- mode preference_for_same_reg(+, +, -, -).
preference_for_same_reg(wait_variable('$VAR'(X),'$VAR'(Y)), Reg, X, Y) :-
    aref(Reg, X, []), aref(Reg, Y, []), !.
preference_for_same_reg(put_value('$VAR'(X),'$VAR'(Y)), Reg, X, Y) :-
    aref(Reg, X, []), aref(Reg, Y, []).

:- mode determine_registers(+, +, +, +, +, +, -, -).
determine_registers(V, V, _, _, R, U, R, U) :- !.      % 88.07.28 Y.Kimura
determine_registers(I, V, From, To, Reg0, Used0, Reg, Used) :-
    aref(Reg0, I, []), !, 
    aref(From, I, F), aref(To, I, T), 
  ( F =\= T, !, 
    find_free_register(R, F, T, Used0, Used1),
    aset(Reg0, I, R, Reg1) ;
    aset(Reg0, I, 0, Reg1), Used1 = Used0 ),		% void 
    I1 is I+1, 
    determine_registers(I1, V, From, To, Reg1, Used1, Reg, Used).
determine_registers(I, V, From, To, Reg0, Used0, Reg, Used) :-
    I1 is I+1,
    determine_registers(I1, V, From, To, Reg0, Used0, Reg, Used).

:- mode find_free_register(-,+,+,+,-).
find_free_register(R, F, T, Used0, Used) :-
    number_of_registers(Max),
    find_free_register(Max, 1, R, F, T, Used0, Used).

:- mode find_free_register(+, +, -, +, +, +, -).
find_free_register(0, _, 0, _, _, Used, Used) :- !,
    error('Unification too much complicated').
find_free_register(_, R, R, F, T, Used0, Used) :-
    register_available(F, T, R, Used0), !,
    use_register(F, T, R, Used0, Used).
find_free_register(K, N, R, F, T, Used0, Used) :-
    K1 is K-1, N1 is N+1,
    find_free_register(K1, N1, R, F, T, Used0, Used).

:- mode register_available(+, +, +, +).
register_available(From, To, R, Used) :-
    LifeTime is To - From,
    register_available_1(LifeTime, From, R, Used).

:- mode register_available_1(+, +, +, +).
register_available_1(0, _, _, _) :- !.
register_available_1(LifeTime, At, R, Used) :-
    aref(Used, At, N),
    (N>>R)/\1 =:= 0,
    LifeTime1 is LifeTime-1, At1 is At+1,
    register_available_1(LifeTime1, At1, R, Used).

:- mode use_register(+, +, +, +, -).
use_register(From, To, R, Used0, Used) :-
    LifeTime is To - From,
    use_register_1(LifeTime, From, R, Used0, Used).

:- mode use_register_1(+, +, +, +, -).
use_register_1(0, _, _, Used, Used) :- !.
use_register_1(LifeTime, At, R, Used0, Used) :-
    aref(Used0, At, N),
    N1 is N\/(1<<R),
    aset(Used0, At, N1, Used1),
    LifeTime1 is LifeTime-1, At1 is At+1,
    use_register_1(LifeTime1, At1, R, Used1, Used).

