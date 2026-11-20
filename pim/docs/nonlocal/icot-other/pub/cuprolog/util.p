repeat.
repeat :- repeat.

%% not(X):-X,!,fail.
%% not(_).

call(X):-execute(X).

append([],X,X).
append([A|X],Y,[A|Z]):-append(X,Y,Z).

member(X,[X|_]).
member(X,[_|Y]):-member(X,Y).

bagof(X,Y,Z) :-gensym('$',Pred), bagof(X,Y,Z,Pred).
bagof(X,Y,Z,Pred) :-  execute(Y),Form=..[Pred,X],assertz(Form),fail.
bagof(_,_,Z,Pred) :- bagof_(Z,Pred).
bagof_([A|B],Pred) :- Form=..[Pred,A],retract(Form),!,bagof_(B,Pred).
bagof_([],_).

reverse(X,Y) :- reverse(X,[],Y).
reverse([A|B],C,X) :- !,reverse(B,[A|C],X).
reverse([],X,X).

fuse([],X,X).
fuse([A|X],Y,[A|Z]):-fuse(X,Y,Z).
fuse(X,[A|Y],[A|Z]):-fuse(X,Y,Z).
fuse([A|X],[A|Y],[A|Z]):-fuse(X,Y,Z).

%% forall(X,Y,Z)  :: forall([X,Y], (man(X),woman(Y)), loves(X,Y))
%% forall(X,Y,Z) :- bagof(X,Y,A), forall_sub(X,A,Z), !.
%% forall_sub(X,[A|B],Z) :- not not forall_sub_sub(X,A,Z),!,forall_sub(X,B,Z).
%% forall_sub(_,[],_).
%% forall_sub_sub(X,X,Z):-Z,!.

%% forall(X,Y) :- not forall_sub(X,Y).
%% forall_sub(X,Y) :- execute(X),forall_sub(Y).
%% forall_sub(Y) :- execute(Y),!,fail.
%% forall_sub(_).

%% consult, reconsult
%%
%% you can use open/3 instead see/1.
%%
consult(X) :- see(X),consult_sub.
consult_sub :- read(X),or((X==end_of_file,seen,!),(consult_sub(X),fail)).
consult_sub((A :- B ; C)) :- !,clause_list(B,BX),clause_list(C,CX),assertz(A,BX,CX).
consult_sub((A :- B)) :- !, clause_list(B,BX), assertz(A,BX).
consult_sub((A ; B)) :- !,clause_list(B,BX), assertz(A,[],BX).
consult_sub(A) :- assertz(A).

reconsult(X) :- see(X),reconsult_sub.
reconsult_sub :-
	read(X),
	or( (X == end_of_file,seen,!, abolish('RECONSULT_TAG',2)),
		(reconsult_sub(X),fail) ).
reconsult_sub((A :- B ; C)) :-!,
	clause_list(B,BX), clause_list(C,CX), reconsult_sub(A,BX,CX).
reconsult_sub((A :- B)) :-!,
	clause_list(B,BX), reconsult_sub(A,BX,[]).
reconsult_sub((A ; B)) :-!,
	clause_list(B,BX), reconsult_sub(A,[],BX).
reconsult_sub(A) :- reconsult_sub(A,[],[]).
reconsult_sub(A,B,C) :-
	functor(A,F,Arity),
	or(('RECONSULT_TAG'(F,Arity)),
		(abolish(F,Arity), assert('RECONSULT_TAG'(F,Arity)))),!,
	assertz(A,B,C),!.

			