/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991,1992.				 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "instr.h"

static CELL const_int0 = {INT, MRBOFF, 0};

#define CheckArguments3(OP,DCOD,IN1,IN2,OUT){\
    register CELL *x;\
    x = IN1;\
    Dereference(x);\
    if(Typeof(x) != INT) goto suspend_or_exception;\
    x = IN2;\
    Dereference(x);\
    if(Typeof(x) != INT){\
  suspend_or_exception:\
	if(IsRef(x)){\
	    register GOAL_RECORD *grec;\
	    register CELL *undef;\
	    GetGoalRecord(grec, 3);\
	    number_of_children++;\
	    grec->parent = parent;\
	    grec->code = (OBJ *)DCOD;\
	    grec->argn = 3;\
	    grec->args[0] = *IN1;\
	    grec->args[1] = *IN2;\
	    AllocUndef(undef);\
	    SetAll(&(grec->args[2]), REF, undef, MRBOFF);\
	    SetGoalPriority(grec, INT, logical_priority);\
	    grec->debug = goal_debug_status;\
	    grec->pcode = current_predicate2 ? current_predicate2\
					     : current_predicate;\
	    single_wait_suspend(grec, x);\
	    SetAll(OUT, REF, undef, MRBOFF);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==IN1 ? 1 : 2),\
				   OP, IIO, IN1, IN2, OUT);\
	}\
	return;\
    }\
}

#define CheckArguments2(OP,DCOD,IN1,OUT){\
    register CELL *x;\
    x = IN1;\
    Dereference(x);\
    if(Typeof(x) != INT){\
	if(IsRef(x)){\
	    register GOAL_RECORD *grec;\
	    register CELL *undef;\
	    GetGoalRecord(grec, 2);\
	    number_of_children++;\
	    grec->parent = parent;\
	    grec->code = (OBJ *)DCOD;\
	    grec->argn = 2;\
	    grec->args[0] = *IN1;\
	    AllocUndef(undef);\
	    SetAll(&(grec->args[1]), REF, undef, MRBOFF);\
	    SetGoalPriority(grec, INT, logical_priority);\
	    grec->debug = goal_debug_status;\
	    grec->pcode = current_predicate2 ? current_predicate2\
					     : current_predicate;\
	    single_wait_suspend(grec, x);\
	    SetAll(OUT, REF, undef, MRBOFF);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1, OP, IO, IN1, OUT);\
	}\
	return;\
    }\
}


/*************************************************************************
*   b_add(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_add()
{
    blt_b_add(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_add(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_ADD, dc_add, in1, in2, out);
#if IGNORE_INTEGER_OVERFLOW
    SetAll(out, INT, Valueof(in1)+Valueof(in2), MRBOFF);
#else
    {
	double x;
	x = (double)Valueof(in1)+(double)Valueof(in2);
	if(IntOverflow(x)){
	    body_builtin_exception(INTEGER_OVERFLOW, 0,
				   KL1B_B_ADD, IIO, in1, in2, out);
	}else{
	    SetAll(out, INT, (int)x, MRBOFF);
	}
    }
#endif
}


/*************************************************************************
*   b_subtract(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_subtract()
{
    blt_b_subtract(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_subtract(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_SUBTRACT, dc_subtract, in1, in2, out);
#if IGNORE_INTEGER_OVERFLOW
    SetAll(out, INT, Valueof(in1)-Valueof(in2), MRBOFF);
#else
    {
	double x;
	x = (double)Valueof(in1)-(double)Valueof(in2);
	if(IntOverflow(x)){
	    body_builtin_exception(INTEGER_OVERFLOW, 0,
				   KL1B_B_SUBTRACT, IIO, in1, in2, out);
	}else{
	    SetAll(out, INT, (int)x, MRBOFF);
	}
    }
#endif
}


/*************************************************************************
*   b_multiply(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_multiply()
{
    blt_b_multiply(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_multiply(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_MULTIPLY, dc_multiply, in1, in2, out);
#if IGNORE_INTEGER_OVERFLOW
    SetAll(out, INT, Valueof(in1)*Valueof(in2), MRBOFF);
#else
    {
	double x;
	x = (double)Valueof(in1)*(double)Valueof(in2);
	if(IntOverflow(x)){
	    body_builtin_exception(INTEGER_OVERFLOW, 0,
				   KL1B_B_MULTIPLY, IIO, in1, in2, out);
	}else{
	    SetAll(out, INT, (int)x, MRBOFF);
	}
    }
#endif
}


/*************************************************************************
*   b_divide(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_divide()
{
    blt_b_divide(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_divide(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_DIVIDE, dc_divide, in1, in2, out);
    if(Valueof(in2) == 0){
	body_builtin_exception(RANGE_OVERFLOW, 2,
			       KL1B_B_DIVIDE, IIO, in1, in2, out);
    }else{
	if(Valueof(in1) == 0x80000000 && Valueof(in2) == -1){
#if IGNORE_INTEGER_OVERFLOW
	    SetAll(out, INT, 0x80000000, MRBOFF);
#else
	    body_builtin_exception(INTEGER_OVERFLOW, 0,
				   KL1B_B_DIVIDE, IIO, in1, in2, out);
#endif
	}else{
	    SetAll(out, INT, Valueof(in1)/Valueof(in2), MRBOFF);
	}
    }
}


/*************************************************************************
*   b_modulo(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_modulo()
{
    blt_b_modulo(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_modulo(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_MODULO, dc_modulo, in1, in2, out);
    if(Valueof(in2) == 0){
	body_builtin_exception(RANGE_OVERFLOW, 2,
			       KL1B_B_MODULO, IIO, in1, in2, out);
    }else{
	if(Valueof(in1) == 0x80000000 && Valueof(in2) == -1){
	    SetAll(out, INT, 0, MRBOFF);
	}else{
	    SetAll(out, INT, Valueof(in1)%Valueof(in2), MRBOFF);
	}
    }
}


/*************************************************************************
*   b_minus(Rin,&Rout)							 *
*************************************************************************/

DCODE dc_minus()
{
    blt_b_minus(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_minus(in1, out)
    CELL *in1, *out;
{
    CheckArguments2(KL1B_B_MINUS, dc_minus, in1, out);
#if !IGNORE_INTEGER_OVERFLOW
    if(Valueof(in1) == 0x80000000){
	body_builtin_exception(INTEGER_OVERFLOW, 0, KL1B_B_MINUS, IO, in1,out);
	return;
    }
#endif
    SetAll(out, INT, -Valueof(in1), MRBOFF);
}


/*************************************************************************
*   b_increment(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_increment()
{
    blt_b_increment(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_increment(in1, out)
    CELL *in1, *out;
{
    CheckArguments2(KL1B_B_INCREMENT, dc_increment, in1, out);
#if !IGNORE_INTEGER_OVERFLOW
    if(Valueof(in1) == 0x7FFFFFFF){
	body_builtin_exception(INTEGER_OVERFLOW, 0,
			       KL1B_B_INCREMENT, IO, in1, out);
	return;
    }
#endif
    SetAll(out, INT, Valueof(in1)+1, MRBOFF);
}


/*************************************************************************
*   b_decrement(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_decrement()
{
    blt_b_decrement(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_decrement(in1, out)
    CELL *in1, *out;
{
    CheckArguments2(KL1B_B_DECREMENT, dc_decrement, in1, out);
#if !IGNORE_INTEGER_OVERFLOW
    if(Valueof(in1) == 0x80000000){
	body_builtin_exception(INTEGER_OVERFLOW, 0,
			       KL1B_B_DECREMENT, IO, in1, out);
	return;
    }
#endif
    SetAll(out, INT, Valueof(in1)-1, MRBOFF);
}


/*************************************************************************
*   b_abs(Rin,^Rout)							 *
*************************************************************************/

DCODE dc_abs()
{
    blt_b_abs(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_abs(in1, out)
    CELL *in1, *out;
{
    CheckArguments2(KL1B_B_ABS, dc_abs, in1, out);
#if !IGNORE_INTEGER_OVERFLOW
    if(Valueof(in1) == 0x80000000){
	body_builtin_exception(INTEGER_OVERFLOW, 0, KL1B_B_ABS, IO, in1, out);
	return;
    }
#endif
    SetAll(out, INT, Valueof(in1)<0?(-Valueof(in1)):Valueof(in1), MRBOFF);
}


/*************************************************************************
*   b_min(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_min()
{
    blt_b_min(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_min(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_MIN, dc_min, in1, in2, out);
    SetAll(out, INT, Valueof(in1)<Valueof(in2)?Valueof(in1)
					      :Valueof(in2), MRBOFF);
}


/*************************************************************************
*   b_max(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_max()
{
    blt_b_max(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_max(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_MAX, dc_max, in1, in2, out);
    SetAll(out, INT, Valueof(in1)>Valueof(in2)?Valueof(in1)
					      :Valueof(in2), MRBOFF);
}


/*************************************************************************
*   b_and(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_and()
{
    blt_b_and(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_and(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_AND, dc_and, in1, in2, out);
    SetAll(out, INT, Valueof(in1)&Valueof(in2), MRBOFF);
}


/*************************************************************************
*   b_or(Rin1,Rin2,^Rout)						 *
*************************************************************************/

DCODE dc_or()
{
    blt_b_or(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_or(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_OR, dc_or, in1, in2, out);
    SetAll(out, INT, Valueof(in1)|Valueof(in2), MRBOFF);
}


/*************************************************************************
*   b_exclusive_or(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_exclusive_or()
{
    blt_b_exclusive_or(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_exclusive_or(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_EXCLUSIVE_OR, dc_exclusive_or, in1, in2, out);
    SetAll(out, INT, Valueof(in1)^Valueof(in2), MRBOFF);
}


/*************************************************************************
*   b_complement(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_complement()
{
    blt_b_complement(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_complement(in1, out)
    CELL *in1, *out;
{
    CheckArguments2(KL1B_B_COMPLEMENT, dc_complement, in1, out);
    SetAll(out, INT, ~Valueof(in1), MRBOFF);
}


/*************************************************************************
*   b_shift_left(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_shift_left()
{
    blt_b_shift_left(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_shift_left(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_SHIFT_LEFT, dc_shift_left, in1, in2, out);
    if((unsigned int)Valueof(in2) >= 32){
	body_builtin_exception(RANGE_OVERFLOW, 2,
			       KL1B_B_SHIFT_LEFT, IIO, in1, in2, out);
    }else{
	SetAll(out, INT, (unsigned int)Valueof(in1)
		       <<(unsigned int)Valueof(in2), MRBOFF);
    }
}


/*************************************************************************
*   b_shift_right(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_shift_right()
{
    blt_b_shift_right(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_shift_right(in1, in2, out)
    CELL *in1, *in2, *out;
{
    CheckArguments3(KL1B_B_SHIFT_RIGHT, dc_shift_right, in1, in2, out);
    if((unsigned int)Valueof(in2) >= 32){
	body_builtin_exception(RANGE_OVERFLOW, 2, 
			       KL1B_B_SHIFT_RIGHT, IIO, in1, in2, out);
    }else{
	SetAll(out, INT, (unsigned int)Valueof(in1)
		       >>(unsigned int)Valueof(in2), MRBOFF);
    }
}


/*************************************************************************
*   b_vector(Rvect,^Rsize,^Rnewvect)					 *
*************************************************************************/

DCODE dc_vector()
{
    blt_b_vector(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_vector(vect, size, newvect)
    CELL *vect, *size, *newvect;
{
    register CELL *x;
    x = vect;
    Dereference(x);
    if(Typeof(x) != VECTOR){
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef1, *undef2;
	    GetGoalRecord(grec, 3);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_vector;
	    grec->argn = 3;
	    grec->args[0] = *vect;
	    AllocUndef(undef1);
	    SetAll(&(grec->args[1]), REF, undef1, MRBOFF);
	    AllocUndef(undef2);
	    SetAll(&(grec->args[2]), REF, undef2, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(size, REF, undef1, MRBOFF);
	    SetAll(newvect, REF, undef2, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_VECTOR, IOO, vect, size, newvect);
	}
    }else{
	register int l = VectorLengthof(vect);
	*newvect = *vect;
	SetAll(size, INT, l, MRBOFF);
    }
}


/*************************************************************************
*   b_new_vector(^Rvect,Rsize)						 *
*************************************************************************/

DCODE dc_new_vector()
{
    blt_b_new_vector(&R2, &R1);
    active_unify(&R0, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_new_vector(vect, size)
    CELL *vect, *size;
{
    register CELL *x;
    x = size;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 2);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_new_vector;
	    grec->argn = 2;
	    grec->args[1] = *size;
	    AllocUndef(undef);
	    SetAll(&(grec->args[0]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(vect, REF, undef, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_NEW_VECTOR, OI, vect, size);
	}
    }else{
	register int n;
	n = Valueof(size);
	if(n < 0 || n >= heap_size){
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_NEW_VECTOR, OI, vect, size);
	    return;
	}
	if(HeapRest() <= n){  /** Enqueue:: Redo after GC **/
	    SetHeapGcFlag();
	    body_builtin_swap(dc_new_vector, OI, vect, size);
	    return;
	}
	AllocVector(x, n);
	SetAll(vect, VECTOR, x, MRBOFF);
	while(n--){
	    *++x = const_int0;
	}
    }
}


/*************************************************************************
*   b_vector_element(Rvect,Rindex,^Relem,^Rnewvect)			 *
*************************************************************************/

DCODE dc_vector_element()
{
    blt_b_vector_element(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_vector_element(vect, pos, elem, newvect)
    CELL *vect, *pos, *elem, *newvect;
{
    register CELL *x;
    x = vect;
    Dereference(x);
    if(Typeof(x) != VECTOR) goto suspend_or_exception;
    x = pos;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef2, *undef3;
	    GetGoalRecord(grec, 4);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_vector_element;
	    grec->argn = 4;
	    grec->args[0] = *vect;
	    grec->args[1] = *pos;
	    AllocUndef(undef2);
	    SetAll(&(grec->args[2]), REF, undef2, MRBOFF);
	    AllocUndef(undef3);
	    SetAll(&(grec->args[3]), REF, undef3, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(elem, REF, undef2, MRBOFF);
	    SetAll(newvect, REF, undef3, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==vect ? 1 : 2),
				   KL1B_B_VECTOR_ELEMENT,
				   IIOO, vect, pos, elem, newvect);
	}
    }else{
	register unsigned p;
	p = Valueof(pos);
	if(p >= (unsigned)VectorLengthof(vect)){
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_VECTOR_ELEMENT,
				   IIOO, vect, pos, elem, newvect);
	    return;
	}
	x = VectorElementof(vect, p);
	Dereference(x);
	SetMrbof(x, MRBON);
	*newvect = *vect;
	*elem = *x;
    }
}


/*************************************************************************
*   b_set_vector_element(Rvect,Rindex,^Roldelem,Relem,^Rnewvect)	 *
*************************************************************************/

DCODE dc_set_vector_element()
{
    blt_b_set_vector_element(&R0, &R1, &R5, &R3, &R6);
    active_unify(&R2, &R5);
    active_unify(&R4, &R6);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_set_vector_element(vect, pos, oldelem, elem, newvect)
    CELL *vect, *pos, *oldelem, *elem, *newvect;
{
    register CELL *x;
    x = vect;
    Dereference(x);
    if(Typeof(x) != VECTOR) goto suspend_or_exception;
    x = pos;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef2, *undef4;
	    GetGoalRecord(grec, 5);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_set_vector_element;
	    grec->argn = 5;
	    grec->args[0] = *vect;
	    grec->args[1] = *pos;
	    grec->args[3] = *elem;
	    AllocUndef(undef2);
	    SetAll(&(grec->args[2]), REF, undef2, MRBOFF);
	    AllocUndef(undef4);
	    SetAll(&(grec->args[4]), REF, undef4, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(oldelem, REF, undef2, MRBOFF);
	    SetAll(newvect, REF, undef4, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==vect ? 1 : (x==pos ? 2 : 4)),
				   KL1B_B_SET_VECTOR_ELEMENT,
				   IIOIO, vect, pos, oldelem, elem, newvect);
	}
    }else{
	register CELL *e;
	register unsigned p, n, i;
	CELL newelem;
	n = VectorLengthof(vect);
	p = Valueof(pos);
	if(p >= n){  /** position is out of range **/
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_SET_VECTOR_ELEMENT,
				   IIOIO, vect, pos, oldelem, elem, newvect);
	    return;
	}
	newelem = *elem;  /* save NewElem */
	if(Mrbof(vect) == MRBOFF){
	    x = VectorElementof(vect, p);
	    *newvect = *vect;
	    *oldelem = *x;
	    *x = newelem;
	    mrbgc_statistics_reuse_in_builtin(n+1);
	}else{
	    if(HeapRest() <= n){  /** Enqueue:: Redo after GC **/
		SetHeapGcFlag();
		body_builtin_swap(dc_set_vector_element,
				  IIOIO, vect, pos, oldelem, elem, newvect);
		return;
	    }
	    x = Objectof(vect)+1;
	    AllocVector(e, n);
	    SetAll(newvect, VECTOR, e, MRBOFF); e++;
	    for(i=0; i<n; i++,x++,e++){
		if(i == p){
		    Dereference(x);
		    SetMrbof(x, MRBON);
		    *oldelem = *x;
		    *e = newelem;
		}else{
		    Dereference(x);
		    SetMrbof(x, MRBON);
		    *e = *x;
		}
	    }
	}
    }
}


/*************************************************************************
*   b_string(Rstr,^Rlength,^Rwidth,^Rnewstr)				 *
*************************************************************************/

DCODE dc_string()
{
    blt_b_string(&R0, &R4, &R5, &R6);
    active_unify(&R1, &R4);
    active_unify(&R2, &R5);
    active_unify(&R3, &R6);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_string(str, len, width, newstr)
    CELL *str, *len, *width, *newstr;
{
    register CELL *x;
    x = str;
    Dereference(x);
    if(Typeof(x) != STRING){
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef1, *undef2, *undef3;
	    GetGoalRecord(grec, 4);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_string;
	    grec->argn = 4;
	    grec->args[0] = *str;
	    AllocUndef(undef1);
	    SetAll(&(grec->args[1]), REF, undef1, MRBOFF);
	    AllocUndef(undef2);
	    SetAll(&(grec->args[2]), REF, undef2, MRBOFF);
	    AllocUndef(undef3);
	    SetAll(&(grec->args[3]), REF, undef3, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(len, REF, undef1, MRBOFF);
	    SetAll(width, REF, undef2, MRBOFF);
	    SetAll(newstr, REF, undef3, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_STRING, IOOO, str,len,width,newstr);
	}
    }else{
	register int type, w, l;
	type = StringTypeof(str);
	w = (1<<(type&7))+(type>>(8-(type&7)));
	l = StringLengthof(str)*(32/w)-((type&(0xFF>>(type&7)))>>3);
	*newstr = *str;
	SetAll(len, INT, l, MRBOFF);
	SetAll(width, INT, w, MRBOFF);
    }
}


/*************************************************************************
*   b_new_string(^Rstr,Rlength,Rwidth)					 *
*************************************************************************/

DCODE dc_new_string()
{
    blt_b_new_string(&R3, &R1, &R2);
    active_unify(&R0, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_new_string(str, len, width)
    CELL *str, *len, *width;
{
    register CELL *x;
    x = len;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = width;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 3);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_new_string;
	    grec->argn = 3;
	    grec->args[1] = *len;
	    grec->args[2] = *width;
	    AllocUndef(undef);
	    SetAll(&(grec->args[0]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(str, REF, undef, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==len ? 2 : 3),
				   KL1B_B_NEW_STRING, OII, str, len, width);
	}
    }else{
	switch(new_string(Valueof(len), Valueof(width), str)){
	  case STRUTL_BAD_LENGTH:
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_NEW_STRING, OII, str, len, width);
	    return;
	  case STRUTL_BAD_WIDTH:
	    body_builtin_exception(RANGE_OVERFLOW, 3,
				   KL1B_B_NEW_STRING, OII, str, len, width);
	    return;
	  case STRUTL_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_new_string, OII, str, len, width);
	    return;
	}
    }
}


/*************************************************************************
*   b_string_element(Rstr,Rindex,^Relem,^Rnewstr)			 *
*************************************************************************/

DCODE dc_string_element()
{
    blt_b_string_element(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_string_element(str, pos, elem, newstr)
    CELL *str, *pos, *elem, *newstr;
{
    register CELL *x;
    x = str;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = pos;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef2, *undef3;
	    GetGoalRecord(grec, 4);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_string_element;
	    grec->argn = 4;
	    grec->args[0] = *str;
	    grec->args[1] = *pos;
	    AllocUndef(undef2);
	    SetAll(&(grec->args[2]), REF, undef2, MRBOFF);
	    AllocUndef(undef3);
	    SetAll(&(grec->args[3]), REF, undef3, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(elem, REF, undef2, MRBOFF);
	    SetAll(newstr, REF, undef3, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==str ? 1 : 2),
				   KL1B_B_STRING_ELEMENT,
				   IIOO, str, pos, elem, newstr);
	}
    }else{
	int element;
	switch(get_string_element(str, Valueof(pos), &element)){
	  case STRUTL_BAD_POSITION:
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_STRING_ELEMENT,
				   IIOO, str, pos, elem, newstr);
	    return;
	  case STRUTL_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_string_element, IIOO, str, pos, elem, newstr);
	    return;
	}
	*newstr = *str;
	SetAll(elem, INT, element, MRBOFF);
    }
}


/*************************************************************************
*   b_set_string_element(Rstr,Rindex,Relem,^Rnewstr)			 *
*************************************************************************/

DCODE dc_set_string_element()
{
    blt_b_set_string_element(&R0, &R1, &R2, &R4);
    active_unify(&R3, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_set_string_element(str, pos, elem, newstr)
    CELL *str, *pos, *elem, *newstr;
{
    register CELL *x;
    x = str;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = pos;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = elem;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 4);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_set_string_element;
	    grec->argn = 4;
	    grec->args[0] = *str;
	    grec->args[1] = *pos;
	    grec->args[2] = *elem;
	    AllocUndef(undef);
	    SetAll(&(grec->args[3]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(newstr, REF, undef, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==str ? 1 : (x==pos ? 2 : 3)),
				   KL1B_B_SET_STRING_ELEMENT,
				   IIIO, str, pos, elem, newstr);
	}
    }else{
	CELL new;
	register int w;
	w = StringTypeof(str);
	w = (1<<(w&7))+(w>>(8-(w&7)));
	if(Valueof(elem)&(0xFFFFFFFE<<(w-1))){
	    body_builtin_exception(RANGE_OVERFLOW, 3,
				   KL1B_B_SET_STRING_ELEMENT,
				   IIIO, str, pos, elem, newstr);
	    return;
	}
	if(Mrbof(str) == MRBON){
	    if(copy_string(str, &new) == STRUTL_REQUEST_GC){
		SetHeapGcFlag();
		body_builtin_swap(dc_set_string_element,
				  IIIO, str, pos, elem, newstr);
		return;
	    }
	    str = &new;
	}else{
	    mrbgc_statistics_reuse_in_builtin(StringLengthof(str)+1);
	}
	if(set_string_element(str, Valueof(pos), Valueof(elem))
	   == STRUTL_BAD_POSITION){
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_SET_STRING_ELEMENT,
				   IIIO, str, pos, elem, newstr);
	    return;
	}
	*newstr = *str;
    }
}


/*************************************************************************
*   b_substring(Rstr,Rindex,Rlength,^Rsubs,^Rnewstr)			 *
*************************************************************************/

DCODE dc_substring()
{
    blt_b_substring(&R0, &R1, &R2, &R5, &R6);
    active_unify(&R3, &R5);
    active_unify(&R4, &R6);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_substring(str, pos, len, substr, newstr)
    CELL *str, *pos, *len, *substr, *newstr;
{
    register CELL *x;
    x = str;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = pos;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = len;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef3, *undef4;
	    GetGoalRecord(grec, 5);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_substring;
	    grec->argn = 5;
	    grec->args[0] = *str;
	    grec->args[1] = *pos;
	    grec->args[2] = *len;
	    AllocUndef(undef3);
	    SetAll(&(grec->args[3]), REF, undef3, MRBOFF);
	    AllocUndef(undef4);
	    SetAll(&(grec->args[4]), REF, undef4, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(substr, REF, undef3, MRBOFF);
	    SetAll(newstr, REF, undef4, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==str ? 1 : (x==pos ? 2 : 3)),
				   KL1B_B_SUBSTRING,
				   IIIOO, str, pos, len, substr, newstr);
	}
    }else{
	CELL new;
	switch(get_substring(str, Valueof(pos), Valueof(len), &new)){
	  case STRUTL_BAD_POSITION:
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_SUBSTRING,
				   IIIOO, str, pos, len, substr, newstr);
	    return;
	  case STRUTL_BAD_LENGTH:
	    body_builtin_exception(RANGE_OVERFLOW, 3,
				   KL1B_B_SUBSTRING,
				   IIIOO, str, pos, len, substr, newstr);
	    return;
	  case STRUTL_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_substring, IIIOO, str,pos,len,substr,newstr);
	    return;
	}
	*newstr = *str;
	*substr = new;
    }
}


/*************************************************************************
*   b_set_substring(Rstr,Rindex,Rsubs,^Rnewstr)				 *
*************************************************************************/

DCODE dc_set_substring()
{
    blt_b_set_substring(&R0, &R1, &R2, &R4);
    active_unify(&R3, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_set_substring(str, pos, substr, newstr)
    CELL *str, *pos, *substr, *newstr;
{
    register CELL *x;
    x = str;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = pos;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = substr;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 4);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_set_substring;
	    grec->argn = 4;
	    grec->args[0] = *str;
	    grec->args[1] = *pos;
	    grec->args[2] = *substr;
	    AllocUndef(undef);
	    SetAll(&(grec->args[3]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(newstr, REF, undef, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==str ? 1 : (x==pos ? 2 : 3)),
				   KL1B_B_SET_SUBSTRING,
				   IIIO, str, pos, substr, newstr);
	}
    }else{
	CELL new;
	if(Mrbof(str) == MRBON){
	    if(copy_string(str, &new) == STRUTL_REQUEST_GC){
		SetHeapGcFlag();
		body_builtin_swap(dc_set_substring,
				  IIIO, str, pos, substr, newstr);
		return;
	    }
	    str = &new;
	}else{
	    mrbgc_statistics_reuse_in_builtin(StringLengthof(str)+1);
	}
	switch(set_substring(str, Valueof(pos), substr)){
	  case STRUTL_BAD_TYPE:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_SET_SUBSTRING,
				   IIIO, str, pos, substr, newstr);
	    return;
	  case STRUTL_BAD_POSITION:
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_SET_SUBSTRING,
				   IIIO, str, pos, substr, newstr);
	    return;
	  case STRUTL_BAD_LENGTH:
	    body_builtin_exception(RANGE_OVERFLOW, 3,
				   KL1B_B_SET_SUBSTRING,
				   IIIO, str, pos, substr, newstr);
	    return;
	}
	if(Mrbof(substr) == MRBOFF){
	    FreeString(Objectof(substr), StringLengthof(substr));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(substr)+1);
	}
	*newstr = *str;
    }
}


/*************************************************************************
*   b_append_string(Rstr1,Rstr2,^Rnewstr)				 *
*************************************************************************/

DCODE dc_append_string()
{
    blt_b_append_string(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_append_string(str1, str2, newstr)
    CELL *str1, *str2, *newstr;
{
    register CELL *x;
    x = str1;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = str2;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 3);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_append_string;
	    grec->argn = 3;
	    grec->args[0] = *str1;
	    grec->args[1] = *str2;
	    AllocUndef(undef);
	    SetAll(&(grec->args[2]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(newstr, REF, undef, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==str1 ? 1 : 2),
				   KL1B_B_APPEND_STRING,
				   IIO, str1, str2, newstr);
	}
    }else{
	CELL new;
	switch(append_string(str1, str2, &new)){
	  case STRUTL_BAD_TYPE:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_APPEND_STRING,
				   IIO, str1, str2, newstr);
	    return;
	  case STRUTL_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_append_string, IIO, str1, str2, newstr);
	    return;
	}
	if(Mrbof(str1) == MRBOFF){
	    FreeString(Objectof(str1), StringLengthof(str1));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(str1)+1);
	}
	if(Mrbof(str2) == MRBOFF){
	    FreeString(Objectof(str2), StringLengthof(str2));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(str2)+1);
	}
	*newstr = new;
    }
}


/*************************************************************************
*   b_string_and(Rstr1,Rstr2,^Rnewstr,^Rnewstr2)			 *
*************************************************************************/

DCODE dc_string_and()
{
    blt_b_string_and(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_string_and(str1, str2, newstr, newstr2)
    CELL *str1, *str2, *newstr, *newstr2;
{
    register CELL *x;
    x = str1;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = str2;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef, *undef2;
	    GetGoalRecord(grec, 4);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_string_and;
	    grec->argn = 4;
	    grec->args[0] = *str1;
	    grec->args[1] = *str2;
	    AllocUndef(undef);
	    SetAll(&(grec->args[2]), REF, undef, MRBOFF);
	    AllocUndef(undef2);
	    SetAll(&(grec->args[3]), REF, undef2, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(newstr, REF, undef, MRBOFF);
	    SetAll(newstr2, REF, undef2, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==str1 ? 1 : 2),
				   KL1B_B_STRING_AND,
				   IIOO, str1, str2, newstr, newstr2);
	}
    }else{
	CELL new, new2;
	switch(string_and(str1, str2, &new, &new2)){
	  case STRUTL_BAD_TYPE:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_STRING_AND,
				   IIOO, str1, str2, newstr, newstr2);
	    return;
	  case STRUTL_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_string_and, IIOO, str1,str2,newstr,newstr2);
	    return;
	}
	*newstr = new;
	*newstr2 = new2;
    }
}


/*************************************************************************
*   b_string_or(Rstr1,Rstr2,^Rnewstr,^Rnewstr2)				 *
*************************************************************************/

DCODE dc_string_or()
{
    blt_b_string_or(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_string_or(str1, str2, newstr, newstr2)
    CELL *str1, *str2, *newstr, *newstr2;
{
    register CELL *x;
    x = str1;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = str2;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef, *undef2;
	    GetGoalRecord(grec, 4);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_string_or;
	    grec->argn = 4;
	    grec->args[0] = *str1;
	    grec->args[1] = *str2;
	    AllocUndef(undef);
	    SetAll(&(grec->args[2]), REF, undef, MRBOFF);
	    AllocUndef(undef2);
	    SetAll(&(grec->args[3]), REF, undef2, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(newstr, REF, undef, MRBOFF);
	    SetAll(newstr2, REF, undef2, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==str1 ? 1 : 2),
				   KL1B_B_STRING_OR,
				   IIOO, str1, str2, newstr, newstr2);
	}
    }else{
	CELL new, new2;
	switch(string_or(str1, str2, &new, &new2)){
	  case STRUTL_BAD_TYPE:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_STRING_OR,
				   IIOO, str1, str2, newstr, newstr2);
	    return;
	  case STRUTL_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_string_or, IIOO, str1, str2, newstr, newstr2);
	    return;
	}
	*newstr = new;
	*newstr2 = new2;
    }
}


/*************************************************************************
*   b_string_exclusive_or(Rstr1,Rstr2,^Rnewstr,^Rnewstr2)		 *
*************************************************************************/

DCODE dc_string_exclusive_or()
{
    blt_b_string_exclusive_or(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_string_exclusive_or(str1, str2, newstr, newstr2)
    CELL *str1, *str2, *newstr, *newstr2;
{
    register CELL *x;
    x = str1;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = str2;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef, *undef2;
	    GetGoalRecord(grec, 4);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_string_exclusive_or;
	    grec->argn = 4;
	    grec->args[0] = *str1;
	    grec->args[1] = *str2;
	    AllocUndef(undef);
	    SetAll(&(grec->args[2]), REF, undef, MRBOFF);
	    AllocUndef(undef2);
	    SetAll(&(grec->args[3]), REF, undef2, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(newstr, REF, undef, MRBOFF);
	    SetAll(newstr2, REF, undef2, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==str1 ? 1 : 2),
				   KL1B_B_STRING_EXCLUSIVE_OR,
				   IIOO, str1, str2, newstr, newstr2);
	}
    }else{
	CELL new, new2;
	switch(string_exclusive_or(str1, str2, &new, &new2)){
	  case STRUTL_BAD_TYPE:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_STRING_EXCLUSIVE_OR,
				   IIOO, str1, str2, newstr, newstr2);
	    return;
	  case STRUTL_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_string_exclusive_or,
			      IIOO, str1, str2, newstr, newstr2);
	    return;
	}
	*newstr = new;
	*newstr2 = new2;
    }
}


/*************************************************************************
*   b_string_complement(Rstr,^Rnewstr)					 *
*************************************************************************/

DCODE dc_string_complement()
{
    blt_b_string_complement(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_string_complement(str, newstr)
    CELL *str, *newstr;
{
    register CELL *x;
    x = str;
    Dereference(x);
    if(Typeof(x) != STRING){
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 2);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_string_complement;
	    grec->argn = 2;
	    grec->args[0] = *str;
	    AllocUndef(undef);
	    SetAll(&(grec->args[1]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(newstr, REF, undef, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_STRING_COMPLEMENT, IO, str, newstr);
	}
    }else{
	CELL new;
	switch(string_complement(str, &new)){
	  case STRUTL_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_string_complement, IO, str, newstr);
	    return;
	}
	*newstr = new;
    }
}


/*************************************************************************
*   b_new_atom(^Ratom)							 *
*************************************************************************/

blt_b_new_atom(atom)
    CELL *atom;
{
    SetAll(atom, ATOM, new_atom(), MRBOFF);
}


/*************************************************************************
*   b_intern_atom(^Ratom,Rstr)						 *
*************************************************************************/

DCODE dc_intern_atom()
{
    blt_b_intern_atom(&R2, &R1);
    active_unify(&R0, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_intern_atom(atom, name)
    CELL *atom, *name;
{
    register CELL *x;
    x = name;
    Dereference(x);
    if(Typeof(x) != STRING){
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 2);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_intern_atom;
	    grec->argn = 2;
	    grec->args[1] = *name;
	    AllocUndef(undef);
	    SetAll(&(grec->args[0]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(atom, REF, undef, MRBOFF);
	}else{
  exception:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_INTERN_ATOM, OI, atom, name);
	}
    }else{
	unsigned int at;
	if(string_to_atom(name, &at) == STRUTL_BAD_TYPE){
	    goto exception;
	}
	if(Mrbof(name) == MRBOFF){
	    FreeString(Objectof(name), StringLengthof(name));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(name)+1);
	}
	SetAll(atom, ATOM, at, MRBOFF);
    }
}


/*************************************************************************
*   b_atom_name(Ratom,^Rstr)						 *
*************************************************************************/

DCODE dc_atom_name()
{
    blt_b_atom_name(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_atom_name(atom, name)
    CELL *atom, *name;
{
    register CELL *x;
    x = atom;
    Dereference(x);
    if(Typeof(x) != ATOM){
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 2);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_atom_name;
	    grec->argn = 2;
	    grec->args[0] = *atom;
	    AllocUndef(undef);
	    SetAll(&(grec->args[1]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(name, REF, undef, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_ATOM_NAME, IO, atom, name);
	}
    }else{
	if(atom_to_string(Valueof(atom), name) == STRUTL_REQUEST_GC){
	    SetHeapGcFlag();
	    body_builtin_swap(dc_atom_name, IO, atom, name);
	    return;
	}
    }
}


/*************************************************************************
*   b_atom_number(Ratom,^Rnumber)					 *
*************************************************************************/

DCODE dc_atom_number()
{
    blt_b_atom_number(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_atom_number(atom, number)
    CELL *atom, *number;
{
    register CELL *x;
    x = atom;
    Dereference(x);
    if(Typeof(x) != ATOM){
	if(IsRef(x)){
	    register GOAL_RECORD *grec;
	    register CELL *undef;
	    GetGoalRecord(grec, 2);
	    number_of_children++;
	    grec->parent = parent;
	    grec->code = (OBJ *)dc_atom_number;
	    grec->argn = 2;
	    grec->args[0] = *atom;
	    AllocUndef(undef);
	    SetAll(&(grec->args[1]), REF, undef, MRBOFF);
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = current_predicate2 ? current_predicate2
					     : current_predicate;
	    single_wait_suspend(grec, x);
	    SetAll(number, REF, undef, MRBOFF);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_ATOM_NUMBER, IO, atom, number);
	}
    }else{
	SetAll(number, INT, Valueof(atom), MRBOFF);
    }
}
