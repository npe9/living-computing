%%%%%%%%%%%%%%%%%%%%%%%% jpsg.p %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%			JPSG parser ver1.3
%%%			1993.7.2
%%%		        JPSG Parser Sample
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%% How to run:
%%      :-parse([ sentence_comes_here ]). as follows:
%%
%%%     :-parse([ken,ga,hon,wo,yom,ase,ta]).
%%%  then the Category for the sentence and
%%%       the constraint for the variables are printed as follows:
%%%
%%%     {head / {mod / M_3272, dep / D_3273, pos / v, form / HForm_3271,
%%%      infl / vv}, adjacent / [], sc / Rest_136, slash / Msl_137,
%%%      sem / SEM_3516}
%%%      c77(SEM_3516, Msl_137, Rest_136, HForm_3271, D_3273, M_3272)
%%%      true.
%%%
%%%   You can get a variety of solutions by refuting the constraint
%%%   as follows:
%%%      :-c77(Sem, SL, SC, F, D, M).

%%%
%%%  Category Definition:
%%%	{head/{pos/Pos, form/Form, gr/Gr, infl/Infl_type,  dep/Dependent,
%%% mod/Flag_of_Modifier}, 
%%	  adjacent/Adjacent, sc/Subcat,
%%	  slash/Slash,  sem/Sem}
%%
%%% Pos: part of speech   p,n,v,adn(rentai-si),adv(huku-si)
%%% Form: when Pos=n, n, ns(sahen-meisi)
%%%	      when Pos=v, root,conj,euph,inf, rel, imp
%%%		  when Pos=p,  ga, wo, ni, ...
%%% Infl: vc,vv,vk,vs,... (verb inflection type), 
%%%		   adj(adjective), na(adjective-verb),nil
%%% Gr:   sbj, obj
%%% Mod:  plus, minus

%%%
%%%  Simple Left Corner Parsing is used as the Stragegy
%%%
parse(S):-parse0(A,B,S,[]),write(A),nl,project_cstr(A),nl.

p2(S):-parse0(A,B,S,[]),nl,write(A),nl,pcon,nl.
p(Sentence):-
	parse0(Cat,H,Sentence,[]),nl,
	tree(H),nl,
	write("category= "),write(Cat),nl,
	write("constraint= "),pcon,nl.

parse0(MCat,MHist,Str,Rest):-
	lookup(Str,SubStr,Cat,Hist),!,
	parse1(Cat,Hist,MCat,MHist,SubStr,Rest).

parse1(LCat,LHist,GCat,GHist,[Word|SubStr],Rest):-
	lookup_post(LCat,Word,RCat,RHist,RuleName),
	psr_adj(LCat,RCat,MCat),
/*	!, */
	parse1(MCat,
		t(t(MCat,RuleName,[]),LHist,RHist),
		GCat,GHist,SubStr,Rest).

parse1(Cat,H,Cat,H,Str,Str).

parse1(LCat,LHist,GCat,GHist,Str,Rest):-
	psr(LCat,RCat,MCat,RN),
	parse0(RCat,RHist,Str,SubStr),
	parse1(MCat,t(t(MCat,RN,[]),LHist,RHist),
		GCat,GHist,SubStr,Rest).

%%%  phrase structure rules
%%%     psr(LeftCat,RightCat,MotherCat)

%%% 1. Adjacent Structure:  psr_adj(Left,Head,Mother)
psr_adj({head/Cc, adjacent/[], sc/Csc, slash/Csl, sem/SEM0},
  {head/Hc, adjacent/[{head/Cc, sc/Asc,sem/SEM0}], sc/Hsc, slash/Hsl, sem/SEM},
  {head/Hc, adjacent/[], sc/Msc, slash/Msl, sem/SEM});
	Cc={mod/minus,dep/{head/Hc}},
	adjacent_sc_p(Csc,Asc,Hsc,Msc),
	slash_p(Csl,Hsl,Msl).

%%  adjacent-subcat principle for adjacent structure
%% adjacent_sc_p(CSC,ASC,HSC,MSC).
%%	CSC=C.sc, ASC=H.adj.sc, HSC=H.sc, MSC=M.sc
%% adjacent_sc_p(CSC,[],HSC,MSC):-merge(CSC,HSC,MSC).
adjacent_sc_p([],[],SC,SC).
adjacent_sc_p([SC|R],[],[],[SC|R]).
adjacent_sc_p(CSC,[AS],HSC,SC):-one_of(CSC,AS,Rest),append(HSC,Rest,SC).
adjacent_sc_p([A1,A2|R],[A1,A2],SC,MSC):-append(SC,R,MSC).  /* for ukemi */

%%% slash feature principle: 
%%%	slash_p(LeftS,RightS,MotherS)
%%%	LeftS=C.slash, RightS=H.slash, MotherS=M.slash
slash_p([],[],[]).
slash_p([S],[],[S]).
slash_p([],[S],[S]).

%%%	2. Subcategorization Structure : psr(C,H,M)
psr(Comp,
    {head/H, adjacent/[], sc/HC, slash/Hsl, sem/Hs},
    {head/H, adjacent/[], sc/Rest,  slash/Msl ,sem/Hs},
	[subcat_p] );
	Comp={head/{dep/{head/H}}, adjacent/[], sc/Csc, slash/Csl},
	one_of(HC,Comp,Rest),
	slash_p(Csl,Hsl,Msl).

%%%	3. Adjunction Structure: psr(An,H,M)
%%  topic should be adjunct?
psr({head/{mod/M,dep/Head}, adjacent/[], slash/Asl, sem/As},
     Head,
    {head/C, adjacent/[],sc/Hsc, slash/Msl,sem/As},
	[adjunct_p] );
	Head={head/C,adjacent/[],sc/Hsc, slash/Hsl, sem/Hs},
	adjunct_slash_p(M,Asl,Hsl,Msl,As).
%%
adjunct_slash_p(plus,Asl,Hsl,Msl,_) :-
		slash_p(Asl,Hsl,Msl).
adjunct_slash_p(topic,[],[{sem/As}],[],As).

%%%%%	lexical rule (for general dictionary)
%%% lex_rule(OrigCat,NewCat)
lex_rule(C,Cat):-
	same_feature(C,Cat),
	adj_mod_default(C,Cat),
	lex_rule_sub(C,Cat).
lex_rule_sub(C,{sc/Nsc,slash/Nsl}) :-
	pvalue(C,sc,S),
	S = [_|_],!;
	sc_sl_shift(S,Nsc,Nsl).
lex_rule_sub(C,{sc/[],slash/[]}).

%% head,sem
same_feature({head/H,sem/S},{head/H,sem/S}).
adj_mod_default(C,Cat) :-
	or((pvalue(C,adjacent,A),Cat={adjacent/A}),
		Cat={adjacent/[]}),
	pvalue(C,head,H),pvalue(Cat,head,HC),
	or((pvalue(H,mod,M),HC={mod/M}),
		HC={mod/minus}).

%% sc,slash (a subcat element shifts to slash) 
%% sc_to_sl({sc/[]},{sc/[],slash/[]}):-!.
sc_to_sl({sc/S},{sc/Nsc,slash/Nsl}):-sc_sl_shift(S,Nsc,Nsl).
%%
sc_sl_shift(Sc,Sc,[]).
sc_sl_shift(Sc,Nsc,[One]):-
	one_of(Sc,One,Nsc).


%%%%%	dictionary lookup in general
%%%%%  lookup(Str,RestStr,Cat,Hist)
lookup([[Sent|Cont]|X],X,Cat,Hist):-
	parse0(Cat,Hist,[Sent|Cont],[]).
lookup([Word|X],X,Cat,t(Cat,[Word],[]))
	:-dict1(Word,C),lex_rule(C,Cat).

%%%%%	pp, suffix, auxiliary verb dictionary
%%%%%	lookup_post(PreCat, Word, PostCat, PostHist,RuleName)
lookup_post(_,Word,Cat,t(Cat,[Word],[]),[adjacent_p])
	:-dict_pos(Word,C), lex_rule(C,Cat).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%	jconst.p 
%%%%%%%%%  constraints
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%	general constraints	   %%%
%%%  constraint  (modular and finite predicates)

%%% one_of(List, One, Rest)    |List|<=3  
one_of([X|Y],X,Y).
one_of([X,Y|Z],Y,[X|Z]).
one_of([X,Y,Z],Z,[X,Y]).

%%%%%%%  constraint (recursive predicate)

merge([],[],[]).
merge([],[A|X],[A|X]).
merge([A|X],[],[A|X]).
merge([A|X],[B|Y],[A|Z]):-merge(X,[B|Y],Z).
merge([B|X],[A|Y],[A|Z]):-merge([B|X],Y,Z).

append([],X,X).
append([A|X],Y,[A|Z]):-append(X,Y,Z).

member(X,[X|Y]).
member(X,[Y|Z]):-member(X,Z).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%		post.p	
%%%	PP, aux , etc.   (have ADJACENT feature)
%%%	dict_pos( 1word, Cat)		: pp, aux, etc.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%	Post Positions
dict_pos(nado,
       	{head/{pos/n,form/Form},sc/[],
	adjacent/[{head/{pos/n,form/Form},sc/[],sem/SEM}],sem/etc(SEM)} ).

%%%%%   Postpositional particles (zyosi)	%%%%%%%%%%%%%%%%%%%%
%%%  --wo,ga,ni,de,to,no,ha,ba
general_pp(Form,
	{head/{pos/p,form/Form},sc/[],
	adjacent/[{head/{pos/n},sc/[],sem/SEM}],sem/SEM} ).
dict_pos(wo, Cat):-general_pp(wo, Cat).
dict_pos(ga, Cat):-general_pp(ga, Cat).
dict_pos(ni, Cat):-general_pp(ni, Cat).

dict_pos(de,
	{head/{pos/adn,form/de,mod/plus,dep/{head/{pos/v},sem/SEM2}},sc/[],
	adjacent/[{head/{pos/n},sc/[],sem/SEM1}],
	sem/de(SEM1,SEM2)} ).

dict_pos(to,
	{head/{pos/Pos,form/to,mod/plus,dep/{head/{pos/Cat2},sem/SEM2}},sc/[],
	adjacent/[{head/{pos/Cat1,form/Form},sc/[],sem/SEM1}],sem/SEM} );
	to_compl(Pos,Cat1,Form,SEM1,Cat2,SEM2,SEM).

to_compl(adj,n,_,S1,v,S2,[with(S1)|S2]).
to_compl(adn,n,_,S1,n,S2,[S1,and|S2]).
to_compl(adj,v,Inf,S1,v,S2, [with,S1,S2] ):-sentence_end(Inf).
sentence_end(inf).
sentence_end(a_inf).
to_compl(adj,v,imp,S1,nil,S2,S1).

dict_pos(no,
       {head/{pos/adn,form/Form,mod/M,dep/Dependent},sc/[],
	adjacent/[{head/{pos/CP,form/CF},sc/[],sem/CS}],sem/SEM} );
	no_handler(CP,CF,Form,M,Dependent,CS,SEM).

no_handler(p,Form,Form,minus,{},Sem,Sem):-
    with_case(Form).
no_handler(n,n,Form,minus,{},Sem,Sem):-
    without_case(Form).
no_handler(n,n,no,plus,
	{head/{pos/n},sc/[],sem/Obj},
           Atr,[Obj,st,[rel,Atr,Obj]]).

dict_pos(ha,
       {head/{pos/p,form/Form},sc/[],
	adjacent/[{head/{pos/Cat,form/F},sc/[],sem/SEM}],sem/SEM} );
       wa_compl(Cat,F,Form).

wa_compl(p,Form,Form):-with_case(Form).
wa_compl(n,_,Form) :- without_case(Form).

with_case(to).
with_case(de).
with_case(he).
with_case(made).
with_case(kara).

without_case(ga).
without_case(wo).

dict_pos(mo,
       {head/{pos/p,form/Form},sc/[],
	adjacent/[{head/{pos/Cat,form/F},sc/[],sem/SEM}],sem/SEM} );
	       mo_compl(Cat,F,Form).

mo_compl(p,wo,wo).
mo_compl(n,F,ga).
mo_compl(p,Form,Form):-with_case(Form).

%%%%%%%%%%%%%%% huku-zyosi
%%%%%%%---ba,temo,demo,te,de,tari,dari,si

dict_pos(ureba,
	{head/{pos/adv,form/katei,mod/plus,dep/{head/{pos/v},sem/SEM2}},sc/[],
	adjacent/[{head/{pos/v,infl/X,form/root},sc/[],sem/SEM1}],
	sem/if(SEM1,SEM2) } ); vs_or_vk(X).
dict_pos(eba,
	{head/{pos/adv,form/katei,mod/plus,dep/{head/{pos/v},sem/SEM2}},sc/[],
	adjacent/[{head/{pos/v,infl/vc,form/root},sc/[],sem/SEM1}],
	sem/if(SEM1,SEM2) } ).
dict_pos(kereba,
	{head/{pos/adv,form/katei,mod/plus,dep/{head/{pos/v},sem/SEM2}},sc/[],
	adjacent/[{head/{pos/v,infl/adj,form/root},sc/[],sem/SEM1}],
	sem/if(SEM1,SEM2) } ).
dict_pos(reba,
	{head/{pos/adv,form/katei,mod/plus,dep/{head/{pos/v},sem/SEM2}},sc/[],
	adjacent/[{head/{pos/v,infl/vv,form/root},sc/[],sem/SEM1}],
	sem/if(SEM1,SEM2) } ).

%%%%	--temo,demo  (even if)
temo_demo(Infl,
	{head/{pos/adv,form/temo,mod/plus,dep/{head/{pos/v},sem/SEM2}},sc/[],
	adjacent/[{head/{pos/v,infl/Infl,form/root},sc/[],sem/SEM1}],
	sem/even_if(SEM1,SEM2) } ).
dict_pos(temo,Cat):-temo_demo(X,Cat); vv_or_euph_vc(X).
dict_pos(itemo,Cat):-temo_demo(X,Cat); vc_vs_or_vk(X).
dict_pos(demo,Cat):-temo_demo(X,Cat); na_or_euph_vc(X).
dict_pos(kutemo,Cat) :- temo_demo(adj,Cat).

na_or_euph_vc(na).
na_or_euph_vc(vc).

vs_or_vk(vs).
vs_or_vk(vk).

%%%%%   --te, de      + iru,miru, etc. 
te_de(X,
	{head/{pos/v,infl/X,form/Y},sc/[],
        adjacent/[{head/{pos/v,infl/X,form/root},sc/[],sem/SEM}],sem/SEM} );
                te_form(Y).
te_form(conj).
te_form(te).
dict_pos(te,Cat):-te_de(X,Cat); vv_or_euph_vc(X).
dict_pos(ite,Cat):-te_de(X,Cat); vc_vs_or_vk(X).
dict_pos(de,Cat):-te_de(X,Cat); na_or_euph_vc(X).
dict_pos(kute,Cat) :- te_de(adj,Cat).


%%%%	--tari,dari  
tari_dari(Form, 
	{head/{pos/adj,form/tari,mod/plus,dep/{head/{pos/vs},sem/SEM2}},sc/[],
	adjacent/[{head/{pos/v,form/Form},sc/[],sem/SEM1}],
	sem/[SEM1|SEM2]} ).

dict_pos(tari,Cat):-tari_dari(X,Cat);vv_or_euph_vc(X).
dict_pos(itari,Cat):-tari_dari(X,Cat); vc_vs_or_vk(X).
dict_pos(dari,Cat):-tari_dari(X,Cat); na_or_euph_vc(X).
dict_pos(kattari,Cat) :- tari_dari(adj,Cat).

%%%%	--si    (--si,--si)
dict_pos(si,
  {head/{pos/adv,form/si,mod/plus,dep/{head/{pos/v,form/Form},sc/[],sem/SEM2}},
  sc/[],adjacent/[{head/{pos/v,form/inf},sc/[],sem/SEM1}],sem/[SEM1|SEM2] } ).
%%%%%%%%%%% weak verbs  
%%%%%	--(te/de)iru,iku,kuru,miru,simawu: stative verbs
stative_verb(INF,A,
	{head/{pos/v,infl/INF,form/root},sc/[],
	adjacent/[{head/{pos/v,form/te},sc/[],sem/Sem}],sem/[A,Sem]}).
dict_pos(i,Cat):-stative_verb(vv,state,Cat).
dict_pos(ik,Cat):-stative_verb(vc,go_to,Cat).
dict_pos(k,Cat):-stative_verb(vk,come_to,Cat).
dict_pos(mi,Cat):-stative_verb(vv,try_to,Cat).
dict_pos(simaw,Cat):-stative_verb(vc,perf,Cat).

%%%%	--dasu,kakeru,hazimeru,owaru,tuzukeru :v(renyou) + v  sub-verb
/*
sub_verb(F,A,
	{head/{pos/v,form/F,mod/minus},sc/[],
	adjacent/[{head/{pos/v,form/Form},sc/[],sem/Sem}],sem/[A|Sem]} );
		tai_set(Form).
dict_pos(das,Cat):-sub_verb(vcs,begin,Cat).
dict_pos(kake,Cat):-sub_verb(vv,nearly,Cat).
dict_pos(hazime,Cat):-sub_verb(vv,begin,Cat).
dict_pos(owar,Cat):-sub_verb(vcr,end,Cat).
dict_pos(tuzuke,Cat):-sub_verb(vv,continue,Cat).
*/
%%%%%%%%%%%%%   Auxiliary verbs (zyo-dousi)	%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%% 	--seru, --saseru : Causative verb (sieki)
sieki_verb(INFL, 
        {head/{pos/v,infl/vv,form/root,mod/minus},
	adjacent/[{head/{pos/v,infl/INFL,form/root},
                sc/[{head/{pos/p,gr/sbj,form/ga},sem/Iob}],sem/Act}],
	sc/[{head/{pos/p,gr/sbj,form/ga},sem/Sbj},
		{head/{pos/p,gr/obj,form/ni},sem/Iob}],
	sem/[cause,Sbj,Iob,Act]} ).

dict_pos(sase,Cat):-sieki_verb(vv,Cat).
dict_pos(ase,Cat):-sieki_verb(Form,Cat);vc_or_vs(Form).
dict_pos(osase,Cat) :- sieki_verb(vk,Cat).
vc_or_vs(vc).
vc_or_vs(vs).

%%%%%	--re(ru), --rare(ru) : Passive verb (ukemi)
dict_pos(rare,Cat):-ukemi_verb(vv,Cat).
dict_pos(are,Cat):-ukemi_verb(Form,Cat);vc_or_vs(Form).
dict_pos(orare,Cat):-ukemi_verb(vk,Cat).

ukemi_verb(INFL,
       {head/{pos/v,infl/vv,form/root,mod/minus},
		adjacent/[{head/{pos/v,infl/INFL,form/root},
		sc/[{head/{pos/p,gr/sbj,form/ga},sem/Agt}|SC],
		sem/Act}],
	sc/[{head/{pos/p,gr/sbj,form/ga},sem/Pat},
		{head/{pos/p,gr/obj,form/ni},sem/Agt}],
	sem/[passive,Pat,Agt,Act]} );
	control_passive(Act,OPT,Pat).

control_passive([_,_],[],_).
control_passive([_,_,Sbj|_],
		[{head/{pos/p,gr/obj,form/Form},sem/Sbj}],Sbj):-obj_case(Form).

obj_case(ni).
obj_case(wo).

%%% general auxirialy verb (syusi,rentai form & others)
%%%   nu, ta,u,you,mai
aux_ren_infl(Infl,Form,A,
  {head/{pos/v,infl/Infl,form/rel,mod/plus,dep/{head/{pos/Pos},sem/X}}, sc/[],
   adjacent/[{head/{pos/v,infl/Infl,form/Form},
	sc/[{head/{pos/p},sem/X}],sem/Sem}],
	slash/[],sem/[X,st,[A,Sem]]}); n_or_p(Pos).
aux_syu_infl(Infl,Form,A,
	{head/{pos/v,infl/Infl,form/inf,mod/minus,sem/X}, sc/[],
	adjacent/[{head/{pos/v,infl/Infl,form/Form},sc/[],sem/Sem}],
	slash/[],sem/[A,Sem]}).
aux_syu_ren_infl(Infl,Form,A,
	{head/{pos/v,infl/Infl,form/HForm,mod/M,dep/D}, sc/[],
	adjacent/[{head/{pos/v,infl/Infl,form/Form},sc/SC,sem/Sem}],
	slash/[],sem/SEM});
	rel_or_inf(HForm,M,D,SC,SEM,[A,Sem]).
rel_or_inf(rel,plus,{head/{pos/Pos},sem/X},[{head/{pos/p},sem/X}],[X,st,Y],Y);
	n_or_p(Pos).
rel_or_inf(inf,minus,{},[],Y,Y).

n_or_p(n).
n_or_p(p).

aux_verb_infl(INFL,FORM,Infl,Form,A,
	{head/{pos/v,infl/INFL,form/FORM,mod/minus},sc/[],
	adjacent/[{head/{pos/v,infl/Infl,form/Form},sc/[],sem/Sem}],
	slash/[],sem/[A,Sem]}).

%%%%%	--na(i),--nu  : Not   
dict_pos(ana,Cat):-aux_verb_infl(adj,root,vc,root,neg,Cat).
dict_pos(na,Cat):-aux_verb_infl(adj,root,vv,root,neg,Cat).
dict_pos(ona,Cat):-aux_verb_infl(adj,root,vk,root,neg,Cat).
dict_pos(ina,Cat):-aux_verb_infl(adj,root,vs,root,neg,Cat). 

dict_pos(on,Cat):-aux_verb_infl(neg,root,vk,root,neg,Cat).
dict_pos(en,Cat):-aux_verb_infl(neg,root,vs,root,neg,Cat).
dict_pos(an,Cat):-aux_verb_infl(neg,root,vc,root,neg,Cat).
dict_pos(n,Cat):-aux_verb_infl(neg,root,vv,root,neg,Cat).

dict_pos(ozu,Cat):-aux_verb_infl(zu,conj,vk,root,neg,Cat).
dict_pos(ezu,Cat):-aux_verb_infl(zu,conj,vs,root,neg,Cat).
dict_pos(azu,Cat):-aux_verb_infl(zu,conj,vc,root,neg,Cat).
dict_pos(zu,Cat):-aux_verb_infl(zu,conj,vv,root,neg,Cat).

%%%%%	--ta,da : Past 
dict_pos(ta,Cat):-aux_syu_ren_infl(X,root,past,Cat); vv_or_euph_vc(X).
dict_pos(ida,Cat):-aux_syu_ren_infl(vc,root,past,Cat).
dict_pos(ita,Cat):-aux_syu_ren_infl(X,root,past,Cat); vc_vs_or_vk(X).
dict_pos(katta,Cat):-aux_syu_ren_infl(adj,root,past,Cat).
dict_pos(datta,Cat):-aux_syu_ren_infl(na,root,past,Cat).
dict_pos(tara,Cat):-aux_verb_infl(X,conj,X,root,past,Cat);vv_or_euph_vc(X).
dict_pos(dara,Cat):-aux_verb_infl(vc,conj,vc,root,past,Cat).
dict_pos(itara,Cat):-aux_verb_infl(X,conj,X,root,past,Cat); vs_or_vk(X).
dict_pos(kattara,Cat):-aux_verb_infl(adj,conj,adj,root,past,Cat).
dict_pos(nara,Cat):-aux_verb_infl(na,conj,na,root,past,Cat).

vv_or_euph_vc(vv).
vv_or_euph_vc(vc).

vc_vs_or_vk(vc).
vc_vs_or_vk(vs).
vc_vs_or_vk(vk).

%%%%%	-(r)u, -i, -da, -na  : Present/Infinitive
dict_pos(i,Cat):-aux_syu_ren_infl(adj,root,pres,Cat).
dict_pos(na,Cat):-aux_ren_infl(na,root,pres,Cat).
dict_pos(da,Cat):-aux_syu_infl(na,root,pres,Cat).
dict_pos(u,Cat):-aux_syu_ren_infl(vc,root,pres,Cat).
dict_pos(uru,Cat):-aux_syu_ren_infl(X,root,pres,Cat); vs_or_vk(X).
dict_pos(ru,Cat):-aux_syu_ren_infl(vv,root,pres,Cat).

%%%%%	--u, --you  : suiryou (guess) or isi(will)
dict_pos(ou,Cat):-aux_verb_infl(vc,inf,vc,root,will,Cat).
dict_pos(you,Cat):-aux_verb_infl(vv,inf,vv,root,will,Cat).
dict_pos(oyou,Cat):-aux_verb_infl(vk,inf,vk,root,will,Cat).
dict_pos(iyou,Cat):-aux_verb_infl(vs,inf,vs,root,will,Cat).
dict_pos(karou,Cat):-aux_verb_infl(adj,inf,adj,root,may,Cat).
dict_pos(darou,Cat):-aux_verb_infl(na,inf,na,root,may,Cat).

%%%%% --rasii : suitei
dict_pos(rasi,Cat):-
        aux_verb_infl(adj,root,Infl,inf,seems,Cat);verb_or_adj(Infl).
dict_pos(rasi,Cat):-
        aux_verb_infl(adj,root,na,root,seems,Cat);verb_or_adj(Infl).

verb_or_adj(adj).
verb_or_adj(vv).
verb_or_adj(vc).
verb_or_adj(vk).
verb_or_adj(vs).

%%%%%%  --mai  : not+guess, not+will
dict_pos(mai,Cat):-aux_syu_ren_infl(mai,inf,Infl,inf,may_not,Cat);verb_set(Infl).
verb_set(vc).
verb_set(vv).
verb_set(vk).
verb_set(vs).

%%%%%%	--ta(i)  : hope		--- need case conversion
dict_pos(ita,Cat):-aux_verb_infl(adj,root,X,root,hope,Cat);verb_set(X).
dict_pos(ta,Cat):-aux_verb_infl(adj,root,vv,root,hope,Cat).

%%%%%  --sou(da). : may & I hear
dict_pos(sou,Cat):-aux_verb_infl(na,root,X,inf,heard_that,Cat); all_verb(X).

all_verb(vv).
all_verb(vc).
all_verb(vk).
all_verb(vs).
all_verb(adj).
all_verb(na).

%%%%%  --desu, masu.	: teinei
desu_set(na,root).
desu_set(adj,inf).
dict_pos(desyo,Cat):-aux_verb_infl(na,inf,X,Y,guess,Cat); desu_set(X,Y).
dict_pos(desita,Cat):-aux_syu_ren_infl(Infl,Form,past,Cat);
		desu_set(Infl,Form).
dict_pos(desu,Cat):-aux_syu_ren_infl(Infl,Form,pres,Cat);
		desu_set(Infl,Form).
/*
masu(Infl,Form,Cat):-aux_verb_infl(masu,Inf,Form,polite,Cat);v_renyou(Form).
dict_pos(mase,Cat):-masu(v_se,Cat).
dict_pos(masyo,Cat):-masu(vc_o,Cat).
dict_pos(masi,Cat):-masu(v_y,Cat).
dict_pos(masu,Cat):-aux_syu_ren(Form,polite,Cat);v_renyou(Form).
dict_pos(masure,Cat):-masu(katei,Cat).
dict_pos(mase,Cat):-masu(imp,Cat).
*/
%%%%%  --nagara, --tsutsu : cont. adverb
dict_pos(inagara,
       {head/{pos/adv,form/adv,mod/plus,dep/{head/{pos/v},sem/SEM1}},sc/[],
	adjacent/[{head/{pos/v,infl/X,form/root},
		sc/[{head/{pos/p,gr/sbj,form/ga},sem/AGT}], sem/SEM}],
	sem/[with,SEM,SEM1]} );
       vc_vs_or_vk(X).
dict_pos(nagara,
       {head/{pos/adv,form/adv,mod/plus,dep/{head/{pos/v},sem/SEM1}},sc/[],
	adjacent/[{head/{pos/v,infl/INFL,form/FORM},
				sc/[{head/{pos/p,gr/sbj,form/ga},sem/AGT}],
				sem/SEM}],
	sem/[with,SEM,SEM1]} );nagara_set(INFL,FORM).

nagara_set(adj,inf).
nagara_set(vv,root).

%%%%%    Suffix ( mizen, renyou, meirei )
suffix_infl(FORM,Infl,Form,
	{head/{pos/v,infl/Infl,form/FORM,mod/minus},sc/[],
	adjacent/[{head/{pos/v,infl/Infl,form/Form},sc/[],sem/Sem}],
	slash/[],sem/Sem}).

dict_pos(ku,Cat):-suffix_infl(conj,adj,root,Cat).
dict_pos(de,Cat):-suffix_infl(conj,na,root,Cat).
dict_pos(ni,Cat):-suffix_infl(conj,na,root,Cat).
dict_pos(i,Cat):-suffix_infl(conj,X,root,Cat);vc_vs_or_vk(X).

%%%	meirei
dict_pos(e,Cat):-suffix_infl(imp,vc,root,Cat).
dict_pos(oi,Cat):-suffix_infl(imp,vk,root,Cat).
dict_pos(iro,Cat):-suffix_infl(imp,vs,root,Cat).
dict_pos(ro,Cat):-suffix_infl(imp,vv,root,Cat).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%% noun.dic %%%%%%%%%%%%%%%%%%%%%%
%%%%%%% common noun, proper nouns %%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%	common nouns.
c_noun(Sem,{head/{pos/n,form/n},sc/[],sem/[Sem,Obj]}).

dict1(ari,Cat):-c_noun(ant,Cat).
dict1(esa,Cat):-c_noun(food,Cat).
dict1(gakushya,Cat):-c_noun(scholar,Cat).
dict1(gyouretu,Cat):-c_noun(row,Cat).
dict1(hana,Cat):-c_noun(flower,Cat).
dict1(hatarakiari,Cat):-c_noun(ari0,Cat).
dict1(hito,Cat):-c_noun(people,Cat).
dict1(hon,Cat):-c_noun(book,Cat).
dict1(isi,Cat):-c_noun(stone,Cat).
dict1(zimen,Cat):-c_noun(ground,Cat).
dict1(katamari,Cat):-c_noun(block,Cat).
dict1(miti,Cat):-c_noun(road,Cat).
dict1(mitisirube,Cat):-c_noun(row,Cat).
dict1(mitisuzi,Cat):-c_noun(road,Cat).
dict1(mokutekiti,Cat):-c_noun(goal,Cat).
dict1(natu,Cat):-c_noun(summer,Cat).
dict1(niwa,Cat):-c_noun(garden,Cat).
dict1(satou,Cat):-c_noun(sugar,Cat).
dict1(soto,Cat):-c_noun(out,Cat).
dict1(sumi,Cat):-c_noun(corner,Cat).
dict1(tubu,Cat):-c_noun(grain,Cat).
dict1(yousu,Cat):-c_noun(yousu,Cat).
dict1(yukute,Cat):-c_noun(way,Cat).

%%%%%%%	proper nouns.
p_noun(Sem,{head/{pos/n,form/n},sem/Sem}).

dict1(amerika,Cat):-p_noun(america,Cat).
dict1(hirosi,Cat):-p_noun(hirosi,Cat).
dict1(ken,Cat):-p_noun(ken,Cat).
dict1(naomi,Cat):-p_noun(naomi,Cat).
dict1(wilson,Cat):-p_noun(wilson,Cat).

%%%%% zibun (self)
%% dict1(zibun, {head/{pos/n,form/n},
%%	refl/[{head/{pos/p,gr/sbj,form/ga},sem/Sem}],
%%	sem/Sem}).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%  verb.dic		  %%%%%%%
%%%%%%  Verbs except sahen-v	%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% vi (|subcat|==1: --ga)
ga_verb(F,Act, 
	{head/{pos/v,infl/F,form/root},
	sc/[{head/{pos/p,gr/sbj,form/ga},sem/Sbj}],
	sem/[Act,Sbj]}).

%%%%% vt (|subcat|==2:)
%%  --ga --wo
ga_wo_verb(F,Act, 
	{head/{pos/v,infl/F,form/root},
	sc/[{head/{pos/p,gr/sbj,form/ga},sem/Sbj},
	    {head/{pos/p,gr/obj,form/wo},sem/Obj}],
	sem/[Act,Sbj,Obj]}).
%%  --ga --ni
ga_ni_verb(F,Act, 
	{head/{pos/v,form/root,infl/F},
	sc/[{head/{pos/p,gr/sbj,form/ga},sem/Sbj},
	    {head/{pos/p,gr/obj,form/ni},sem/Obj}],
	sem/[Act,Sbj,Obj]}).

%%  --ga --wo --ni
ga_wo_ni_verb(F,Act, 
	{head/{pos/v,form/root,infl/F},
	sc/[{head/{pos/p,gr/sbj,form/ga},sem/Sbj},
	    {head/{pos/p,gr/obj,form/wo},sem/Iob},
	    {head/{pos/p,gr/obj,form/ni},sem/Dob}],
	sem/[Act,Sbj,Iob,Dob]}).

%%% lexical entry
dict1(age,Cat):-ga_wo_ni_verb(vv,give,Cat).
dict1(ais,Cat):-ga_wo_verb(vc,love,Cat).
dict1(ake,Cat):-ga_wo_verb(vv,open,Cat),temp1(Cat).
dict1(aruk,Cat):-ga_verb(vc,walk,Cat).
dict1(tigaw,Cat):-ga_verb(vc,differ,Cat).
dict1(tirzirininar,Cat):-ga_verb(vc,scatter,Cat).
dict1(deki,Cat):-ga_verb(vv,can,Cat).
dict1(der,Cat):-ga_ni_verb(vv,out,Cat).
dict1(hasir,Cat):-ga_verb(vc,run,Cat).
dict1(hazure,Cat):-ga_wo_verb(vv,off,Cat).
dict1(i,Cat):-ga_verb(vv,be,Cat).
dict1(ik,Cat):-ga_ni_verb(vc,go,Cat).
dict1(isog,Cat):-ga_verb(vc,hurry,Cat).
dict1(kaer,Cat):-ga_ni_verb(vc,return,Cat).
dict1(kag,Cat):-ga_wo_verb(vc,smell,Cat).
dict1(kak,Cat):-ga_wo_verb(vc,write,Cat).
dict1(kaw,Cat):-ga_wo_verb(vc,buy,Cat).
dict1(kawar,Cat):-ga_verb(vc,lose,Cat).
dict1(kat,Cat):-ga_ni_verb(vc,win,Cat).
dict1(ker,Cat):-ga_wo_verb(vv,kick,Cat).
dict1(ki,Cat):-ga_wo(vv,wear,Cat),temp1(Cat).
dict1(maziwar,Cat):-ga_verb(vc,cross,Cat).
dict1(manab,Cat):-ga_wo_verb(vc,learn,Cat).
dict1(mayow,Cat):-ga_verb(vc,maze,Cat).
dict1(mi,Cat):-ga_wo_verb(vv,look_at,Cat).
dict1(midare,Cat):-ga_verb(vv,confuse,Cat).
dict1(mituke,Cat):-ga_wo_verb(vv,find,Cat).
dict1(mot,Cat):-ga_wo_verb(vc,have,Cat).
dict1(nar,Cat):-ga_ni_verb(vv,become,Cat).
dict1(nor,Cat):-ga_ni_verb(vc,on,Cat).
dict1(ok,Cat):-ga_wo_ni_verb(vc,put,Cat).
dict1(omow,Cat):-ga_wo_verb(vc,think,Cat).
dict1(os,Cat):-ga_wo_verb(vc,push,Cat).
dict1(saegi,Cat):-ga_wo_verb(vc,interrupt,Cat).
dict1(sagas,Cat):-ga_wo_verb(vc,search,Cat).
dict1(sir,Cat):-ga_wo_verb(vc,know,Cat).
dict1(sin,Cat):-ga_verb(vc,die,Cat).
dict1(susum,Cat):-ga_ni_verb(vc,go,Cat).
dict1(tador,Cat):-ga_wo_verb(vc,follow,Cat).
dict1(tasuker,Cat):-ga_wo_verb(vv,help,Cat).
dict1(toor,Cat):-ga_ni_verb(vc,pass,Cat).
dict1(tuger,Cat):-ga_wo_ni_verb(vv,tell,Cat).
dict1(tuk,Cat):-ga_ni_verb(vc,reach,Cat).
dict1(tuzuku,Cat):-ga_verb(vc,continue,Cat).
dict1(wakar,Cat):-ga_wo_verb(vc,understand,Cat).
dict1(yom,Cat):-ga_wo_verb(vc,read,Cat).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%	sahen.dic
%%%%%	sahen-n,v dictionary
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%% sahen constraint %%%%%%%%%%%%%%%%%%%
%%			suru(Adjacent,Subcat,Sem)			%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% suru_verb({head/{pos/v,infl/vs,form/root},adjacent/[],sc/SC,sem/Sem}); 
%%%		suru(SC,Sem).
%%% dict1(s,Cat):-suru_verb(Cat).

suru([{head/{pos/p,gr/obj,form/wo},
		  sc/[{head/{pos/adn,gr/sbj,form/ga},sem/Sbj}],
		  sem/[Pred,Sbj | SRest]},
	{head/{pos/p,gr/sbj,form/ga},sem/Sbj}],
     [Pred,Sbj | SRest]).
suru([{head/{pos/p,gr/obj,form/wo}, sc/[], sem/Obj},
        {head/{pos/p,gr/obj,form/ni}, sc/[], sem/State},
	{head/{pos/p,gr/sbj,form/ga}, sc/[], sem/Sbj}],
     [make,Sbj,Obj,State]). 

suru_correspond([],[],[]).
suru_correspond([Sbj], [{head/{form/F},sem/Sbj}], 
	[{head/{pos/p,form/F},sem/Sbj}]).
suru_correspond([Sbj,Obj], 
	[{head/{form/FO},sem/Obj},{head/{form/FS},sem/Sbj}], 
	[{head/{pos/p,form/FS},sem/Sbj},{head/{pos/p,form/FO},sem/Obj}]).
suru_correspond([Sbj,Obj,Iob],
  [{head/{form/FO},sem/Obj},{head/{form/FI},sem/Iob},{head/{form/FS},sem/Sbj}],
	[{head/{pos/p,form/FS},sem/Sbj},
	{head/{pos/p,form/FI},sem/Iob},
	{head/{pos/p,form/FO},sem/Obj}]).


%%%%%	verb : SURU
dict1(s,{head/{pos/v,infl/vs,form/root},adjacent/[],sc/SC,sem/Sem});
        suru(SC,Sem).
dict_pos(s,
	{head/{pos/v,infl/vs,form/root},
	 adjacent/[{head/{pos/n,form/ns},sc/Subc,sem/[Pred|SRest]}],
	 sc/SC,sem/[Pred|SRest]});
		suru_correspond(SRest,Subc,SC).

%%%%%	sa-hen nouns, which can be sa-hen verbs.
sahen_noun([Act,Sbj],
 {head/{pos/n,form/ns},sc/[{head/{pos/adn,gr/sbj},sem/Sbj}],sem/[Act,Sbj]} ).
sahen_noun([Act,Sbj,Obj],
	{head/{pos/n,form/ns},
	 sc/[{head/{pos/adn,gr/obj},sem/Obj},{head/{pos/adn,gr/sbj},sem/Sbj}],
	 sem/[Act,Sbj,Obj]} ).

dict1(tanzyou,Cat):-sahen_noun([birth,X],Cat).
dict1(tyousa,Cat):-sahen_noun([examine,X,Y],Cat). 
dict1(kenkyu,Cat):-sahen_noun([study,X,Y],Cat).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%   adject.dic
%%%%%	adjective, adjective-verb
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%   Adjectives	%%%%%%%%%%%%%
adjective(A,
	{head/{pos/v,infl/adj,form/root},
	sc/[{head/{pos/p,gr/sbj,form/ga},sem/Obj}],
	sem/[A,Obj]} ).
dict1(aka,Cat):-adjective(red,Cat).
dict1(siro,Cat):-adjective(white,Cat).
dict1(kuro,Cat):-adjective(black,Cat).
dict1(ooki,Cat):-adjective(big,Cat).
dict1(yo,Cat):-adjective(good,Cat).

%%%%%	na (adjective-verb)
ajverb(A,
	{head/{pos/v,form/root,infl/na},
	sc/[{head/{pos/p,gr/sbj,form/ga},sem/Obj}],
	sem/[A,Obj]} ).
dict1(kirei,Cat):-ajverb(beautifle,Cat).
dict1(kaiteki,Cat):-ajverb(confortable,Cat).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%		etc.dic
%%%%%%%		dictionary of other words
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%% rentai-shi
rentaisi(A,
	{head/{pos/adn, form/adn}, 
	dep/[{head/{pos/n,form/n},adjacent/[],dep/[],sc/[],sem/SEM}], 
	sem/[A|SEM]}
).
dict1(sono,Cat):-rentaisi(the,Cat).
dict1(kono,Cat):-rentaisi(this,Cat).
dict1(ano,Cat):-rentaisi(that,Cat).
dict1(ippikino,Cat):-rentaisi(one,Cat).

%%%%%%% fuku-shi (adverb)

adverb(MODIFY, 
	{head/{pos/adv, form/root, dep/{head/{pos/v},sem/SEM}}, 
	sem/[MODIFY,SEM]}).
dict1(yoku,Cat):-adverb(often,Cat).
dict1(zutto,Cat):-adverb(continue,Cat).
dict1(hazimeni,Cat):-adverb(first,Cat).
dict1(sukosi,Cat):-adverb(slightly,Cat).
dict1(yagate,Cat):-adverb(in_the_end,Cat).
dict1(tugitugito,Cat):-adverb(continue,Cat).
dict1(dandanni,Cat):-adverb(gradually,Cat).
dict1(komakani,Cat):-adverb(minutely,Cat).
dict1(kessite,
	{head/{pos/adv, dep/{head/{pos/v},sem/[neg,SEM]}},
	sem/[never,SEM]}).
