/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
/* PORT: forward declarations */
static int terminate_merger();
static int make_unify_goal_and_enqueue_for_merger();


static CELL work;


/*************************************************************************
*   General Unification.  X=Y.						 *
*************************************************************************/

active_unify(regX, regY)
    CELL *regX, *regY;
{
    register CELL *varY;
    Dereference2(regY, varY);
    switch(Typeof(varY)){
      case ATOM:
	active_unify_with_atom(regX, Valueof(varY));
	return;
      case INT:
	active_unify_with_integer(regX, Valueof(varY));
	return;
      case FLOAT:
	active_unify_with_float(regX, Valueof(varY));
	return;
      case LIST:
	active_unify_with_list(regX, varY);
	return;
      case VECTOR:
	active_unify_with_vector(regX, varY);
	return;
      case STRING:
	active_unify_with_string(regX, varY);
	return;
      case NUE:
	active_unify_with_nue(regX, varY);
	return;
      case SHOEN:
	active_unify_with_shoen(regX, Shoenof(varY));
	return;
      case UNDEF:
	active_unify_with_undef(regX, varY, Mrbof(regY));
	return;
      case HOOK:
	active_unify_with_hook(regX, varY, Mrbof(regY));
	return;
      case MHOOK:
	active_unify_with_mhook(regX, varY, Mrbof(regY));
	return;
      case MGHOK:
	active_unify_with_stream(regX, varY, Mrbof(regY));
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(varY);
	exception_active_unify_fail(regX, regY);
    }
}


/*************************************************************************
*   Active Unification with Constant.					 *
*************************************************************************/

active_unify_with_atom(reg, atom)
    CELL *reg;
    unsigned int atom;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case ATOM:
	if(Valueof(var) == atom) return;
      case INT: case FLOAT: case LIST: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto unify_fail;
      case UNDEF:
	SetAll(var, ATOM, atom, Mrbof(reg));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, ATOM, atom, Mrbof(reg));
	return;
      case MGHOK:
	if(atom == NIL){
	    active_unify_stream_nil(var, Mrbof(reg));
	}else{
	    active_unify_stream_atom(var, Mrbof(reg), atom);
	}
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	SetAll(&work, ATOM, atom, MRBOFF);
	exception_active_unify_fail(reg, &work);
    }
}

active_unify_with_nil(reg)
    CELL *reg;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case ATOM:
	if(Valueof(var) == NIL) return;
      case INT: case FLOAT: case LIST: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto unify_fail;
      case UNDEF:
	SetAll(var, ATOM, NIL, Mrbof(reg));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, ATOM, NIL, Mrbof(reg));
	return;
      case MGHOK:
	active_unify_stream_nil(var, Mrbof(reg));
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	exception_active_unify_fail(reg, &const_nil);
    }
}

active_unify_with_integer(reg, inte)
    CELL *reg;
    int inte;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case INT:
	if(Valueof(var) == inte) return;
      case ATOM: case FLOAT: case LIST: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto unify_fail;
      case UNDEF:
	SetAll(var, INT, inte, Mrbof(reg));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, INT, inte, Mrbof(reg));
	return;
      case MGHOK:
	active_unify_stream_integer(var, Mrbof(reg), inte);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	SetAll(&work, INT, inte, MRBOFF);
	exception_active_unify_fail(reg, &work);
    }
}

active_unify_with_float(reg, flot)
    CELL *reg;
    int flot;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case FLOAT:
	if(Valueof(var) == flot) return;
      case ATOM: case INT: case LIST: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto unify_fail;
      case UNDEF:
	SetAll(var, FLOAT, flot, Mrbof(reg));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, FLOAT, flot, Mrbof(reg));
	return;
      case MGHOK:
	active_unify_stream_float(var, Mrbof(reg), flot);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	SetAll(&work, FLOAT, flot, MRBOFF);
	exception_active_unify_fail(reg, &work);
    }
}

active_unify_with_list(reg, list)
    CELL *reg, *list;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case LIST:
	make_unify_list_list_goal_and_enqueue(var, list);
	return;
      case INT: case FLOAT: case ATOM: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto unify_fail;
      case UNDEF:
	SetAll(var, LIST, Objectof(list), Mrbof(reg)|Mrbof(list));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, LIST, Objectof(list), Mrbof(reg)|Mrbof(list));
	return;
      case MGHOK:
	active_unify_stream_list(var, Mrbof(reg), list);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	exception_active_unify_fail(reg, list);
    }
}

active_unify_with_vector(reg, vct)
    CELL *reg, *vct;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case VECTOR:
	if(VectorLengthof(var) == VectorLengthof(vct)){
	    make_unify_vector_vector_goal_and_enqueue(var, vct);
	    return;
	}
      case INT: case FLOAT: case ATOM: case LIST: case STRING:
      case NUE: case SHOEN:
	goto unify_fail;
      case UNDEF:
	SetAll(var, VECTOR, Objectof(vct), Mrbof(reg)|Mrbof(vct));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, VECTOR, Objectof(vct), Mrbof(reg)|Mrbof(vct));
	return;
      case MGHOK:
	active_unify_stream_vector(var, Mrbof(reg), vct);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	exception_active_unify_fail(reg, vct);
    }
}

active_unify_with_string(reg, str)
    CELL *reg;
    register CELL *str;
{
    register CELL *var, *ptr;
    register int  size;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case STRING:
	size = StringLengthof(var);
	if(size == StringLengthof(str)){
	    var = Objectof(var);
	    ptr = Objectof(str);
	    while(size-- >= 0){
		if(Valueof(var) != Valueof(ptr)) goto unify_fail;
		var++; ptr++;
	    }
	    return;
	}
      case INT: case FLOAT: case ATOM: case LIST: case VECTOR:
      case NUE: case SHOEN:
	goto unify_fail;
      case UNDEF:
	SetAll(var, STRING, Objectof(str), Mrbof(reg)|Mrbof(str));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, STRING, Objectof(str), Mrbof(reg)|Mrbof(str));
	return;
      case MGHOK:
	active_unify_stream_string(var, Mrbof(reg), str);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	exception_active_unify_fail(reg, str);
    }
}

active_unify_with_nue(reg, nue)
    CELL *reg, *nue;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case NUE:
	if(Objectof(var) == Objectof(nue)) return;
      case INT: case FLOAT: case ATOM: case LIST: case VECTOR: case STRING:
      case SHOEN:
	goto unify_fail;
      case UNDEF:
	SetAll(var, NUE, Objectof(nue), Mrbof(reg)|Mrbof(nue));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, NUE, Objectof(nue), Mrbof(reg)|Mrbof(nue));
	return;
      case MGHOK:
	active_unify_stream_nue(var, Mrbof(reg), nue);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	exception_active_unify_fail(reg, nue);
    }
}

active_unify_with_shoen(reg, shoen)
    CELL *reg;
    PARENT_RECORD *shoen;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case SHOEN:
	if(Shoenof(var) == shoen) return;
      case INT: case FLOAT: case ATOM: case LIST: case VECTOR: case STRING:
      case NUE:
	goto unify_fail;
      case UNDEF:
	SetAll(var, SHOEN, shoen, Mrbof(reg));
	return;
      case HOOK: case MHOOK:
	wakeup_goals(var, SHOEN, shoen, Mrbof(reg));
	return;
      case MGHOK:
	active_unify_stream_shoen(var, Mrbof(reg), shoen);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      unify_fail:
	SetAll(&work, SHOEN, shoen, MRBOFF);
	exception_active_unify_fail(reg, &work);
    }
}


/*************************************************************************
*   Active Unification with Variable.					 *
*************************************************************************/

active_unify_with_undef(reg, undef, mrb)
    CELL *reg, *undef;
    MRB	 mrb;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case ATOM: case INT: case FLOAT: case SHOEN:
	SetAll(undef, Typeof(var), Valueof(var), mrb);
	return;
      case LIST: case VECTOR: case STRING: case NUE:
	SetAll(undef, Typeof(var), Objectof(var), Mrbof(reg)|mrb);
	return;
      case UNDEF:
	if(var != undef) SetAll(var, REF, undef, Mrbof(reg)|mrb);
	return;
      case HOOK:
	DetectDeadlockInUnifyHookUndef(var, Mrbof(reg), undef, mrb);
	SetAll(undef, REF, var, Mrbof(reg)|mrb);
	return;
      case MGHOK:
	DetectDeadlockInUnifyMghokUndef(var, Mrbof(reg), undef, mrb);
	SetAll(undef, REF, var, Mrbof(reg)|mrb);
	return;
      case MHOOK:
	SetAll(undef, REF, var, Mrbof(reg)|mrb);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
	SetAll(&work, REF, undef, mrb);
	exception_active_unify_fail(reg, &work);
    }
}

active_unify_with_hook(reg, hook, mrb)
    CELL *reg, *hook;
    MRB	 mrb;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case INT: case ATOM: case FLOAT: case SHOEN:
	wakeup_goals(hook, Typeof(var), Valueof(var), mrb);
	return;
      case LIST: case VECTOR: case STRING: case NUE:
	wakeup_goals(hook, Typeof(var), Objectof(var), Mrbof(reg)|mrb);
	return;
      case UNDEF:
	DetectDeadlockInUnifyHookUndef(hook, mrb, var, Mrbof(reg));
	SetAll(var, REF, hook, Mrbof(reg)|mrb);
	return;
      case HOOK:
	if(var == hook) return;
	DetectDeadlockInUnifyHookHook(hook, mrb, var, Mrbof(reg));
      case MHOOK:
	move_suspension_queue(var, hook);
	SetAll(var, REF, hook, Mrbof(reg)|mrb);
	return;
      case MGHOK:
	DetectDeadlockInUnifyHookMghok(hook, mrb, var, Mrbof(reg));
	active_unify_stream_hook(var, Mrbof(reg), hook, mrb);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
	SetAll(&work, REF, hook, mrb);
	exception_active_unify_fail(reg, &work);
    }
}

active_unify_with_mhook(reg, mhook, mrb)
    CELL *reg, *mhook;
    MRB	 mrb;
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case INT: case ATOM: case FLOAT: case SHOEN:
	wakeup_goals(mhook, Typeof(var), Valueof(var), mrb);
	return;
      case LIST: case VECTOR: case STRING: case NUE:
	wakeup_goals(mhook, Typeof(var), Objectof(var), Mrbof(reg)|mrb);
	return;
      case UNDEF:
	SetAll(var, REF, mhook, Mrbof(reg)|mrb);
	return;
      case MHOOK:
	if(var == mhook) return;
      case HOOK:
	move_suspension_queue(var, mhook);
	SetAll(var, REF, mhook, Mrbof(reg)|mrb);
	return;
      case MGHOK:
	active_unify_stream_hook(var, Mrbof(reg), mhook, mrb);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
	SetAll(&work, REF, mhook, mrb);
	exception_active_unify_fail(reg, &work);
    }
}

active_unify_with_stream(reg, stream, mrb)
    CELL *reg, *stream;
    MRB	 mrb;		
{
    register CELL *var;
    Dereference2(reg, var);
    switch(Typeof(var)){
      case ATOM:
	if(Valueof(var) == NIL){
	    active_unify_stream_nil(stream, mrb);
	}else{
	    active_unify_stream_atom(stream, mrb, Valueof(var));
	}
	return;
      case INT:
	active_unify_stream_integer(stream, mrb, Valueof(var));
	return;
      case FLOAT:
	active_unify_stream_float(stream, mrb, Valueof(var));
	return;
      case LIST:
	active_unify_stream_list(stream, mrb, var);
	return;
      case VECTOR:
	active_unify_stream_vector(stream, mrb, var);
	return;
      case STRING:
	active_unify_stream_string(stream, mrb, var);
	return;
      case NUE:
	active_unify_stream_nue(stream, mrb, var);
	return;
      case SHOEN:
	active_unify_stream_shoen(stream, mrb, Shoenof(var));
	return;
      case UNDEF:
	DetectDeadlockInUnifyMghokUndef(stream, mrb, var, Mrbof(reg));
	SetAll(var, REF, stream, Mrbof(reg)|mrb);
	return;
      case HOOK:
	DetectDeadlockInUnifyHookMghok(var, Mrbof(reg), stream, mrb);
      case MHOOK:
	active_unify_stream_hook(stream, mrb, var, Mrbof(reg));
	return;
      case MGHOK:
	DetectDeadlockInUnifyMghokMghok(stream, mrb, var, Mrbof(reg));
	active_unify_stream_stream(stream, var);
	return;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
	SetAll(&work, REF, stream, mrb);
	exception_active_unify_fail(reg, &work);
    }
}


/*************************************************************************
*   Active Unification with Stream.					 *
*************************************************************************/

active_unify_stream_atom(strm, mrb, atom)
    CELL *strm;
    MRB	 mrb;
    int	 atom;	/** atom \= [] **/
{
    CELL x, y, *mghok;
    if(IsParentAborted(Mergerof(strm)->parent)){
	if(mrb == MRBON) SetAll(strm, ATOM, atom, MRBON);
	return;
    }
    if(mrb == MRBOFF){
	SetAll(&y, REF, strm, MRBOFF);
    }else{
	AllocMghok(mghok);
	SetMergerof(mghok, Mergerof(strm));
	SetAll(&y, REF, mghok, MRBOFF);
	SetAll(strm, ATOM, atom, MRBON);
    }
    SetAll(&x, ATOM, atom, MRBOFF);
    Error("Stream = Atom(=\\= [])");
    exception_illegal_merger_input(&x, &y);
}

active_unify_stream_nil(strm, mrb)
    CELL *strm;
    MRB	 mrb;
{
    register MERGER_RECORD *merger;
    merger = Mergerof(strm);
    if(IsParentAborted(merger->parent)){
	if(mrb == MRBON) SetAll(strm, ATOM, NIL, MRBON);
	return;
    }
    if(--(merger->count) == 0){
	register CELL *reg, *var;
	reg = &(merger->output);
	Dereference2(reg, var);
	switch(Typeof(var)){
	  case UNDEF:
	    SetAll(var, ATOM, NIL, Mrbof(reg));
	    break;
	  case HOOK: case MHOOK:
	    wakeup_goals(var, ATOM, NIL, Mrbof(reg));
	    break;
	  case ATOM:
	    if(Valueof(var) == NIL) break;
	  DEFAULT:
	    make_unify_goal_and_enqueue_for_merger(
		Typeof(reg),Objectof(reg),Mrbof(reg), ATOM,NIL,MRBOFF, merger);
	}
	terminate_merger(merger);
    }
    if(mrb == MRBOFF){
	FreeCell(strm);
	mrbgc_statistics_collect_in_builtin(1);
    }else{
	SetAll(strm, ATOM, NIL, MRBON);
    }
}

active_unify_stream_integer(strm, mrb, inte)
    CELL *strm;
    MRB	 mrb;
    int	 inte;
{
    CELL x, y, *mghok;
    if(IsParentAborted(Mergerof(strm)->parent)){
	if(mrb == MRBON) SetAll(strm, INT, inte, MRBON);
	return;
    }
    if(mrb == MRBOFF){
	SetAll(&y, REF, strm, MRBOFF);
    }else{
	AllocMghok(mghok);
	SetMergerof(mghok, Mergerof(strm));
	SetAll(&y, REF, mghok, MRBOFF);
	SetAll(strm, INT, inte, MRBON);
    }
    SetAll(&x, INT, inte, MRBOFF);
    Error("Stream = Integer");
    exception_illegal_merger_input(&x, &y);
}

active_unify_stream_float(strm, mrb, flot)
    CELL *strm;
    MRB	 mrb;
    int	 flot;
{
    CELL x, y, *mghok;
    if(IsParentAborted(Mergerof(strm)->parent)){
	if(mrb == MRBON) SetAll(strm, FLOAT, flot, MRBON);
	return;
    }
    if(mrb == MRBOFF){
	SetAll(&y, REF, strm, MRBOFF);
    }else{
	AllocMghok(mghok);
	SetMergerof(mghok, Mergerof(strm));
	SetAll(&y, REF, mghok, MRBOFF);
	SetAll(strm, FLOAT, flot, MRBON);
    }
    SetAll(&x, FLOAT, flot, MRBOFF);
    Error("Stream = Floating Point");
    exception_illegal_merger_input(&x, &y);
}

active_unify_stream_list(strm, mrb, list)
    CELL *strm, *list;
    MRB	 mrb;
{ 
    register CELL *incdr, *outcdr, *cons, *outvp, *outvar, *tailvar;
    CELL tmp;
    MERGER_RECORD *merger;
    merger = Mergerof(strm);
    if(IsParentAborted(merger->parent)){
	if(mrb == MRBON) SetAll(strm, LIST, Objectof(list), MRBON);
	return;
    }
    if(mrb == MRBOFF && Mrbof(list) == MRBOFF){
	/** MGHOK cell & LIST cell are SRP -> Reuse cons cell **/
	/**** Search Tail of SRP List & Cut off SRP List from Input ****/
	/*
	Before:
		  +------+    +------+	  +------+    +------+
	  list--->|LIST O+--->|	     | +->|	 | +->|	     |
		  +------+    +------+ |  +------+ |  +------+	  +------+
			      |LIST O+-+  |LIST O+-+  |REF  -+--->|UNDEF |
			      +------+	  +------+    +------+	  +------+

	After:
	  cons-------------+
		  +------+ +->+------+	  +------+	+------+
	  list--->|LIST O+--->|	     | +->|	 | +--->|      |
		  +------+    +------+ |  +------+ |	+------+    +------+
			      |LIST O+-+  |LIST O+-+ +->|      | +->|UNDEF |
			      +------+	  +------+   |	+------+ |  +------+
						     |		 | 
					    outcdr---+	+------+ |
					     incdr----->|REF  -+-+
							+------+
							tmp
	*/
	cons = Carof(list);
	outcdr = Cdrof(list);
	Dereference(outcdr);
	mrbgc_statistics_reuse_in_merger();
	while(Typeof(outcdr) == LIST && Mrbof(outcdr) == MRBOFF){
	    outcdr = Cdrof(outcdr);
	    Dereference(outcdr);
	    mrbgc_statistics_reuse_in_merger();
	}
	tmp = *outcdr;
	incdr = &tmp;
    }else{
	/**** Make CONS cell for Merger Output ****/
	/*
	Before:
		  +------+	+------+       +------+
	  list--->|LIST X+----->|     -+-+  +->|      |
		  +------+	+------+ |  |  +------+	   
				|LIST -+-|--+  |LIST -+-->
				+------+ |     +------+	   
					 +-->+--------+
					     |CAR-DATA|
					     +--------+
	After:
		  +------+	+------+       +------+
	  list--->|LIST X+----->|     X+-+  +->|      |
		  +------+	+------+ |  |  +------+	   
			     +->|LIST X+-|--+  |LIST -+-->
			     |	+------+ |     +------+	   
		      incdr--+		 +-->+--------+
				New Cons +-->|CAR-DATA|
				+------+ |   +--------+
		      cons----->|     X+-+
				+------+
		      outcdr--->|      |
				+------+
	*/
	AllocCons(cons);
	incdr = Carof(list);  /* use incdr temporary */
	Dereference(incdr);
	SetMrbof(incdr, MRBON);
	cons[0] = *incdr;  /** Copy CAR **/
	outcdr = &cons[1];
	incdr = Cdrof(list);
	Dereference(incdr);
	SetMrbof(incdr, MRBON);
    }
    AllocUndef(tailvar);
    SetAll(outcdr, REF, tailvar, MRBOFF);
    /**** Unify New Cons with Merger Output ****/
    outvp = &(merger->output);
    Dereference2(outvp, outvar);
    switch(Typeof(outvar)){
      case UNDEF:
	SetAll(outvar, LIST, cons, Mrbof(outvp));
	break;
      case HOOK: case MHOOK:
	wakeup_goals(outvar, LIST, cons, Mrbof(outvp));
	break;
      DEFAULT:
	make_unify_goal_and_enqueue_for_merger(
	 Typeof(outvp),Objectof(outvp),Mrbof(outvp), LIST,cons,MRBOFF, merger);
    }
    /**** Unify LIST with Old Merger Input Variable ****/
    if(mrb == MRBON){
	AllocMghok(cons);  /* use cons temporary */
	SetMergerof(cons, merger);
	SetAll(strm, LIST, Objectof(list), MRBON);
	strm = cons;
    }
    /**** Unify Tail with New Merger Input ****/
    if(Typeof(incdr) == REF && Typeof(Objectof(incdr)) == UNDEF){
	merger->output = *outcdr;
	SetAll(Objectof(incdr), REF, strm, Mrbof(incdr));
    }else if(Typeof(incdr) == ATOM && Valueof(incdr) == NIL){
	if(--(merger->count) == 0){
	    SetAll(tailvar, ATOM, NIL, MRBOFF);
	    terminate_merger(merger);
	}else{
	    merger->output = *outcdr;
	}
    }else{
	merger->output = *outcdr;
	make_unify_goal_and_enqueue_for_merger(
	  Typeof(incdr),Objectof(incdr),Mrbof(incdr), REF,strm,MRBOFF, merger);
    }
}

active_unify_stream_vector(strm, mrb, vct)
    CELL *strm, *vct;
    MRB	 mrb;
{
    register CELL *mgs, *vp;
    MERGER_RECORD *merger;
    unsigned size, i;
    merger = Mergerof(strm);
    vp = Objectof(vct);
    if(IsParentAborted(merger->parent)){
	if(mrb == MRBON) SetAll(strm, VECTOR, vp, MRBON);
	return;
    }
    if((size = VectorLengthof(vct)) != 0){
	if(mrb == MRBON) SetAll(strm, VECTOR, vp, MRBON);
	vp++;  /* Skip descriptor */
	if(mrb == MRBOFF && Mrbof(vct) == MRBOFF){
	    for(i=size; i; i--,vp++){
		Dereference(vp);
		AllocMghok(mgs);
		SetMergerof(mgs, merger);
		make_unify_goal_and_enqueue_for_merger(
		    Typeof(vp),Objectof(vp),Mrbof(vp), REF,mgs,MRBOFF, merger);
	    }
	    FreeVector(Objectof(vct), size);
	    mrbgc_statistics_collect_in_builtin(size+1);
	}else{
	    for(i=size; i; i--,vp++){
		Dereference(vp);
		SetMrbof(vp, MRBON);
		AllocMghok(mgs);
		SetMergerof(mgs, merger);
		make_unify_goal_and_enqueue_for_merger(
			Typeof(vp),Objectof(vp),MRBON, REF,mgs,MRBOFF, merger);
	    }
	}
	merger->count += size-1;  /* increment reference count */
    }else{
	if(--(merger->count) == 0){
	    register CELL *reg, *var;
	    reg = &(merger->output);
	    Dereference2(reg, var);
	    switch(Typeof(var)){
	      case UNDEF:
		SetAll(var, ATOM, NIL, Mrbof(reg));
		break;
	      case HOOK: case MHOOK:
		wakeup_goals(var, ATOM, NIL, Mrbof(reg));
		break;
	      case ATOM:
		if(Valueof(var) == NIL) break;
	      DEFAULT:
		make_unify_goal_and_enqueue_for_merger(
					 Typeof(reg),Objectof(reg),Mrbof(reg),
						      ATOM,NIL,MRBOFF, merger);
	    }
	    terminate_merger(merger);
	}
	if(mrb == MRBOFF){
	    if(Mrbof(vct) == MRBOFF){
		FreeVector(vp, 0);
		mrbgc_statistics_collect_in_builtin(1);
	    }
	    FreeCell(strm);
	    mrbgc_statistics_collect_in_builtin(1);
	}else{
	    SetAll(strm, VECTOR, vp, MRBON);
	}
    }
}

active_unify_stream_string(strm, mrb, str)
    CELL *strm, *str;
    MRB	 mrb;
{
    CELL x, *mghok;
    if(IsParentAborted(Mergerof(strm)->parent)){
	if(mrb == MRBON){ SetMrbof(str, MRBON); *strm = *str; }
	return;
    }
    if(mrb == MRBOFF){
	SetAll(&x, REF, strm, MRBOFF);
    }else{
	AllocMghok(mghok);
	SetMergerof(mghok, Mergerof(strm));
	SetAll(&x, REF, mghok, MRBOFF);
	SetMrbof(str, MRBON);
	*strm = *str;
    }
    Error("Stream = String");
    exception_illegal_merger_input(str, &x);
}

active_unify_stream_nue(strm, mrb, nue)
    CELL *strm, *nue;
    MRB	 mrb;
{
    CELL x, *mghok;
    if(IsParentAborted(Mergerof(strm)->parent)){
	if(mrb == MRBON){ SetMrbof(nue, MRBON); *strm = *nue; }
	return;
    }
    if(mrb == MRBOFF){
	SetAll(&x, REF, strm, MRBOFF);
    }else{
	AllocMghok(mghok);
	SetMergerof(mghok, Mergerof(strm));
	SetAll(&x, REF, mghok, MRBOFF);
	SetMrbof(nue, MRBON);
	*strm = *nue;
    }
    Error("Stream = Nue");
    exception_illegal_merger_input(nue, &x);
}

active_unify_stream_shoen(strm, mrb, shoen)
    CELL *strm;
    MRB	 mrb;
    PARENT_RECORD *shoen;
{
    CELL x, y, *mghok;
    if(IsParentAborted(Mergerof(strm)->parent)){
	if(mrb == MRBON) SetAll(strm, SHOEN, shoen, MRBON);
	return;
    }
    if(mrb == MRBOFF){
	SetAll(&y, REF, strm, MRBOFF);
    }else{
	AllocMghok(mghok);
	SetMergerof(mghok, Mergerof(strm));
	SetAll(&y, REF, mghok, MRBOFF);
	SetAll(strm, SHOEN, shoen, MRBON);
    }
    SetAll(&x, SHOEN, shoen, MRBOFF);
    Error("Stream = Shoen");
    exception_illegal_merger_input(&x, &y);
}

active_unify_stream_hook(strm, mrbst, hook, mrbhk)
    CELL *hook, *strm;
    MRB mrbhk, mrbst;
{
    register CELL *mghok;
    register MERGER_RECORD *merger;
    register GOAL_RECORD *grec;
    merger = Mergerof(strm);
    if(IsParentAborted(merger->parent)){
	if(mrbst == MRBON) SetAll(strm, REF, hook, MRBON);
	return;
    }
    if(mrbst == MRBON){
	AllocMghok(mghok);
	SetMergerof(mghok, merger);
	SetAll(strm, REF, hook, MRBON);
	strm = mghok;
    }
    grec = make_unify_goal_for_merger(REF,hook,mrbhk, REF,strm,MRBOFF, merger);
    SetGoalQueuePt(grec, Typeof(hook), Goalof(hook));
    if(Typeof(hook) == MHOOK){
	SetSuspRecBackward(Suspof(hook), HOOK, grec);
    }
    SetTypeof(hook, HOOK); SetGoalof(hook, grec);
}

active_unify_stream_stream(st1, st2)
    CELL *st1, *st2;
{
    register CELL *mghk1, *mghk2;
    register MERGER_RECORD *mg1, *mg2;
    register GOAL_RECORD *grec1, *grec2;
    mg1 = Mergerof(st1);
    if(IsParentAborted(mg1->parent)){
	SetAll(st1, REF, st2, MRBON);
	return;
    }
    mg2 = Mergerof(st2);
    if(IsParentAborted(mg2->parent)){
	SetAll(st2, REF, st1, MRBON);
	return;
    }
    AllocMghok(mghk1);
    SetMergerof(mghk1, mg1);
    AllocMghok(mghk2);
    SetMergerof(mghk2, mg2);
    SetAll(st1, REF, st2, MRBON);
    grec1 = make_unify_goal_for_merger(REF,st2,MRBON, REF,mghk1,MRBOFF, mg1);
    grec2 = make_unify_goal_for_merger(REF,st2,MRBON, REF,mghk2,MRBOFF, mg2);
    SetTypeof(st2, HOOK); SetGoalof(st2, grec1);
    SetGoalQueuePt(grec1, HOOK, grec2);
    SetGoalQueuePt(grec2, UNDEF, NULL);
}

static terminate_merger(merger)
    MERGER_RECORD *merger;
{
    PARENT_RECORD *current_shoen;
    current_shoen = parent;
    CacheParent2(merger->parent);
    if(--number_of_children == 0){
	terminate_shoen();
	parent = NULL;
    }
    CacheParent2(current_shoen);
}


/*************************************************************************
*   Create D-Code Goal.							 *
*************************************************************************/

GOAL_RECORD *make_unify_goal_for_merger(type1, val1, mrb1,
					type2, val2, mrb2, merger)
    TYPE type1, type2;
    CELL *val1, *val2;
    MRB	 mrb1,	mrb2;
    MERGER_RECORD *merger;
{
    register GOAL_RECORD *grec;
    PARENT_RECORD *current_shoen;
    current_shoen = parent;
    CacheParent2(merger->parent);
    GetGoalRecord(grec, 2);
    number_of_children++;
    grec->parent = parent;
    grec->code = (OBJ *)dc_unify;
    grec->argn = 2;
    SetAll(&(grec->args[0]), type1, val1, mrb1);
    SetAll(&(grec->args[1]), type2, val2, mrb2);
    SetGoalPriority(grec, INT, merger->priority);
    grec->debug = NO_TRACE_GOAL;
    grec->pcode = merger->pcode;
    CacheParent2(current_shoen);
    return(grec);
}

static make_unify_goal_and_enqueue_for_merger(type1, val1, mrb1,
					      type2, val2, mrb2, merger)
    TYPE type1, type2;
    CELL *val1, *val2;
    MRB	 mrb1,	mrb2;
    MERGER_RECORD *merger;
{
    register GOAL_RECORD *grec;
    PARENT_RECORD *current_shoen;
    current_shoen = parent;
    CacheParent2(merger->parent);
    GetGoalRecord(grec, 2);
    number_of_children++;
    grec->parent = parent;
    grec->code = (OBJ *)dc_unify;
    grec->argn = 2;
    SetAll(&(grec->args[0]), type1, val1, mrb1);
    SetAll(&(grec->args[1]), type2, val2, mrb2);
    SetGoalPriority(grec, INT, merger->priority);
    grec->debug = NO_TRACE_GOAL;
    grec->pcode = merger->pcode;
    enqueue_with_priority(grec);
    CacheParent2(current_shoen);
}

make_unify_list_list_goal_and_enqueue(x, y)
    CELL *x, *y;
{
    register GOAL_RECORD *grec;
    GetGoalRecord(grec, 2);
    number_of_children++;
    grec->parent = parent;
    grec->code = (OBJ *)dc_unify_list_list2;
    grec->argn = 2;
    grec->args[0] = *x;
    grec->args[1] = *y;
    SetGoalPriority(grec, INT, logical_priority);
    grec->debug = NO_TRACE_GOAL;
    grec->pcode = current_predicate2 ? current_predicate2 : current_predicate;
    enqueue(grec);
}

make_unify_vector_vector_goal_and_enqueue(x, y)
    CELL *x, *y;
{
    register GOAL_RECORD *grec;
    GetGoalRecord(grec, 3);
    number_of_children++;
    grec->parent = parent;
    grec->code = (OBJ *)dc_unify_vector_vector2;
    grec->argn = 3;
    grec->args[0] = *x;
    grec->args[1] = *y;
    SetAll(&(grec->args[2]), INT, 0, MRBOFF);
    SetGoalPriority(grec, INT, logical_priority);
    grec->debug = NO_TRACE_GOAL;
    grec->pcode = current_predicate2 ? current_predicate2 : current_predicate;
    enqueue(grec);
}


/*************************************************************************
*   D-Code for Active Unification.					 *
*************************************************************************/

DCODE dc_unify()
{
    active_unify(&R0, &R1);
    CountDcodeReduction();
    return(NC_PROCEED);
}

DCODE dc_unify_list_list()
{
    register CELL *x;
    register GOAL_RECORD *grec;
    x = &R0;
    Dereference(x);
    if(Typeof(x) != LIST) goto suspend_or_fail;
    x = &R1;
    Dereference(x);
    if(Typeof(x) != LIST){
  suspend_or_fail:
	if(IsRef(x)){
	    GetGoalRecord(grec, 2);
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_unify_list_list;
	    grec->argn = 2;
	    grec->args[0] = R0;
	    grec->args[1] = R1;
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2;
	    single_wait_suspend(grec, x);
	    return(NC_SUSPENDED);
	}
	return(NC_FAIL);
    }
    return(dc_unify_list_list2());
}

DCODE dc_unify_list_list2()
{
    register CELL *lp1, *lp2;
    register MRB  mrb1, mrb2;
    lp1 = Carof(&R0); mrb1 = Mrbof(&R0);
    lp2 = Carof(&R1); mrb2 = Mrbof(&R1);
    Dereference(lp1); if(mrb1 == MRBON) SetMrbof(lp1, MRBON);
    Dereference(lp2); if(mrb2 == MRBON) SetMrbof(lp2, MRBON);
    active_unify(lp1, lp2);
    lp1++; lp2++;
    Dereference(lp1); if(mrb1 == MRBON) SetMrbof(lp1, MRBON);
    Dereference(lp2); if(mrb2 == MRBON) SetMrbof(lp2, MRBON);
    active_unify(lp1, lp2);
    if(mrb1 == MRBOFF){
	FreeCons(lp1-1); mrbgc_statistics_collect_in_builtin(2);
    }
    if(mrb2 == MRBOFF){
	FreeCons(lp2-1); mrbgc_statistics_collect_in_builtin(2);
    }
    CountDcodeReduction();
    return(NC_PROCEED);
}

DCODE dc_unify_vector_vector()
{
    register CELL *x;
    register GOAL_RECORD *grec;
    x = &R0;
    Dereference(x);
    if(Typeof(x) != VECTOR) goto suspend_or_fail;
    x = &R1;
    Dereference(x);
    if(Typeof(x) != VECTOR) goto suspend_or_fail;
    x = &R2;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_fail:
	if(IsRef(x)){
	    GetGoalRecord(grec, 3);
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_unify_vector_vector;
	    grec->argn = 3;
	    grec->args[0] = R0;
	    grec->args[1] = R1;
	    grec->args[2] = R2;
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2;
	    single_wait_suspend(grec, x);
	    return(NC_SUSPENDED);
	}
	return(NC_FAIL);
    }
    if(VectorLengthof(&R0) == VectorLengthof(&R1) || Valueof(x) < 0){
	return(NC_FAIL);
    }
    return(dc_unify_vector_vector2());
}

DCODE dc_unify_vector_vector2()
{
    register CELL *vp1, *vp2, *v;
    register MRB  mrb1, mrb2;
    register int  i, j, size, start;
    vp1 = Objectof(&R0)+1; mrb1 = Mrbof(&R0);
    vp2 = Objectof(&R1)+1; mrb2 = Mrbof(&R1);
    start = Valueof(&R2);
    size = VectorLengthof(&R0);
    for(i = start; i < size; i++){
	if(InterruptOccurred() || HeapRest()<size){
	    if(mrb1 == MRBON){
		AllocVector(v, size);
		SetAll(&R0, VECTOR, v, MRBOFF);
		for(j=0; j<i; j++) *++v = const_nil;
		for(; j<size; j++){
		    Dereference(&vp1[j]); SetMrbof(&vp1[j], MRBON);
		    *++v = vp1[j];
		}
	    }else{
		for(j=start; j<i; j++) vp1[j] = const_nil;
	    }
	    if(mrb2 == MRBON){
		AllocVector(v, size);
		SetAll(&R1, VECTOR, v, MRBOFF);
		for(j=0; j<i; j++) *++v = const_nil;
		for(; j<size; j++){
		    Dereference(&vp2[j]); SetMrbof(&vp2[j], MRBON);
		    *++v = vp2[j];
		}
	    }else{
		for(j=start; j<i; j++) vp2[j] = const_nil;
	    }
	    SetAll(&R2, INT, i, MRBOFF);
	    SetHeapGcFlag();
	    return(NC_SWAPGOAL);
	}
	Dereference(vp1+i); if(mrb1 == MRBON) SetMrbof(vp1+i, MRBON);
	Dereference(vp2+i); if(mrb2 == MRBON) SetMrbof(vp2+i, MRBON);
	active_unify(vp1+i, vp2+i);
    }
    if(mrb1 == MRBOFF){
	FreeVector(vp1-1, size); mrbgc_statistics_collect_in_builtin(size+1);
    }
    if(mrb2 == MRBOFF){
	FreeVector(vp2-1, size); mrbgc_statistics_collect_in_builtin(size+1);
    }
    CountDcodeReduction();
    return(NC_PROCEED);
}


/*************************************************************************
*   Display Error Message.						 *
*************************************************************************/

illegal_data_type_in_active_unify(x)
    CELL *x;
{
    Error1F("Illegal type (%d) data is found in active unify!!", Typeof(x));
}
