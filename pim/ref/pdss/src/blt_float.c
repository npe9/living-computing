/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "instr.h"


/*************************************************************************
*   g_float_add(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_add(in1, in2, out)
    CELL *in1, *in2, *out;
{
    int z;
    if(float_add(&Valueof(in1), &Valueof(in2), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_subtract(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_subtract(in1, in2, out)
    CELL *in1, *in2, *out;
{
    int z;
    if(float_subtract(&Valueof(in1), &Valueof(in2), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_multiply(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_multiply(in1, in2, out)
    CELL *in1, *in2, *out;
{
    int z;
    if(float_multiply(&Valueof(in1), &Valueof(in2), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_divide(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_divide(in1, in2, out)
    CELL *in1, *in2, *out;
{
    int z;
    if(float_divide(&Valueof(in1), &Valueof(in2), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_minus(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_minus(in, out)
    CELL *in, *out;
{
    int z;
    if(float_minus(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_abs(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_abs(in, out)
    CELL *in, *out;
{
    int z;
    float_abs(&Valueof(in), &z);
    SetAll(out, FLOAT, z, MRBOFF);
    return(YES);
}


/*************************************************************************
*   g_float_min(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_min(in1, in2, out)
    CELL *in1, *in2, *out;
{
    int z;
    float_min(&Valueof(in1), &Valueof(in2), &z);
    SetAll(out, FLOAT, z, MRBOFF);
    return(YES);
}


/*************************************************************************
*   g_float_max(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_max(in1, in2, out)
    CELL *in1, *in2, *out;
{
    int z;
    float_max(&Valueof(in1), &Valueof(in2), &z);
    SetAll(out, FLOAT, z, MRBOFF);
    return(YES);
}


/*************************************************************************
*   g_float_floor(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_floor(in, out)
    CELL *in, *out;
{
    int z;
    if(float_floor(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_sqrt(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_sqrt(in, out)
    CELL *in, *out;
{
    int z;
    if(float_sqrt(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_ln(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_ln(in, out)
    CELL *in, *out;
{
    int z;
    if(float_ln(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_log(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_log(in, out)
    CELL *in, *out;
{
    int z;
    if(float_log(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_exp(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_exp(in, out)
    CELL *in, *out;
{
    int z;
    if(float_exp(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_pow(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_pow(in1, in2, out)
    CELL *in1, *in2, *out;
{
    int z;
    if(float_pow(&Valueof(in1), &Valueof(in2), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_sin(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_sin(in, out)
    CELL *in, *out;
{
    int z;
    if(float_sin(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_cos(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_cos(in, out)
    CELL *in, *out;
{
    int z;
    if(float_cos(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_tan(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_tan(in, out)
    CELL *in, *out;
{
    int z;
    if(float_tan(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_asin(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_asin(in, out)
    CELL *in, *out;
{
    int z;
    if(float_asin(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_acos(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_acos(in, out)
    CELL *in, *out;
{
    int z;
    if(float_acos(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_atan(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_atan(in, out)
    CELL *in, *out;
{
    int z;
    if(float_atan(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_atan2(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_atan2(in1, in2, out)
    CELL *in1, *in2, *out;
{
    int z;
    if(float_atan2(&Valueof(in1), &Valueof(in2), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_sinh(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_sinh(in, out)
    CELL *in, *out;
{
    int z;
    if(float_sinh(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_cosh(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_cosh(in, out)
    CELL *in, *out;
{
    int z;
    if(float_cosh(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_tanh(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_tanh(in, out)
    CELL *in, *out;
{
    int z;
    if(float_tanh(&Valueof(in), &z)){
	SetAll(out, FLOAT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }
}


/*************************************************************************
*   g_float_to_integer(Rin,^Rout)					 *
*************************************************************************/

int blt_g_float_to_integer(in, out)
    CELL *in, *out;
{
    int z;
    if(float_to_integer(&Valueof(in), &z)){
	SetAll(out, INT, z, MRBOFF);
	return(YES);
    }else{
	return(NO);
    }

}


/*************************************************************************
*   g_integer_to_float(Rin,^Rout)					 *
*************************************************************************/

int blt_g_integer_to_float(in, out)
    CELL *in, *out;
{
    int z;
    integer_to_float(&Valueof(in), &z);
    SetAll(out, FLOAT, z, MRBOFF);
    return(YES);
}


/*************************************************************************
*   Macros for Body Builtin.						 *
*************************************************************************/

#define DEF3D(BLT){\
    BLT(&R0, &R1, &R3);\
    active_unify(&R2, &R3);\
    CountDcodeReduction();\
    return(NC_PROCEED);\
}

#define DEF3B(FN, IN1, IN2, OUT, DC, OP){\
    register CELL *x;\
    x = IN1;\
    Dereference(x);\
    if(Typeof(x) != FLOAT) goto suspend_or_exception;\
    x = IN2;\
    Dereference(x);\
    if(Typeof(x) != FLOAT){\
  suspend_or_exception:\
	if(IsRef(x)){\
	    body_builtin_suspend(DC, x, IIO, IN1, IN2, OUT);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==IN1 ? 1 : 2),\
				   OP, IIO, IN1, IN2, OUT);\
	}\
    }else{\
	int *z;\
	if(FN(&Valueof(IN1), &Valueof(IN2), &z)){\
	    SetAll(OUT, FLOAT, z, MRBOFF);\
	}else{\
	    body_builtin_exception(FLOATING_ERROR, 0, OP, IIO, IN1, IN2, OUT);\
	}\
    }\
}

#define DEF3BN(FN, IN1, IN2, OUT, DC, OP){\
    register CELL *x;\
    x = IN1;\
    Dereference(x);\
    if(Typeof(x) != FLOAT) goto suspend_or_exception;\
    x = IN2;\
    Dereference(x);\
    if(Typeof(x) != FLOAT){\
  suspend_or_exception:\
	if(IsRef(x)){\
	    body_builtin_suspend(DC, x, IIO, IN1, IN2, OUT);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==IN1 ? 1 : 2),\
				   OP, IIO, IN1, IN2, OUT);\
	}\
    }else{\
	int *z;\
	FN(&Valueof(IN1), &Valueof(IN2), &z);\
	SetAll(OUT, FLOAT, z, MRBOFF);\
    }\
}

#define DEF2D(BLT){\
    BLT(&R0, &R2);\
    active_unify(&R1, &R2);\
    CountDcodeReduction();\
    return(NC_PROCEED);\
}

#define DEF2B(FN, IN, OUT, DC, OP){\
    Dereference(IN);\
    if(Typeof(IN) != FLOAT){\
	if(IsRef(IN)){\
	    body_builtin_suspend(DC, IN, IO, IN, OUT);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1, OP, IO, IN, OUT);\
	}\
    }else{\
	int *z;\
	if(FN(&Valueof(IN), &z)){\
	    SetAll(OUT, FLOAT, z, MRBOFF);\
	}else{\
	    body_builtin_exception(FLOATING_ERROR, 0, OP, IO, IN, OUT);\
	}\
    }\
}

#define DEF2BN(FN, IN, OUT, DC, OP){\
    Dereference(IN);\
    if(Typeof(IN) != FLOAT){\
	if(IsRef(IN)){\
	    body_builtin_suspend(DC, IN, IO, IN, OUT);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1, OP, IO, IN, OUT);\
	}\
    }else{\
	int *z;\
	FN(&Valueof(IN), &z);\
	SetAll(OUT, FLOAT, z, MRBOFF);\
    }\
}


/*************************************************************************
*   b_float_add(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_add()
{
    DEF3D(blt_b_float_add);
}

blt_b_float_add(in1, in2, out)
    CELL *in1, *in2, *out;
{
    DEF3B(float_add, in1, in2, out, dc_float_add, KL1B_B_FLOAT_ADD);
}


/*************************************************************************
*   b_float_subtract(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_subtract()
{
    DEF3D(blt_b_float_subtract);
}

blt_b_float_subtract(in1, in2, out)
    CELL *in1, *in2, *out;
{
    DEF3B(float_subtract,in1,in2,out, dc_float_subtract,KL1B_B_FLOAT_SUBTRACT);
}


/*************************************************************************
*   b_float_multiply(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_multiply()
{
    DEF3D(blt_b_float_multiply);
}

blt_b_float_multiply(in1, in2, out)
    CELL *in1, *in2, *out;
{
    DEF3B(float_multiply,in1,in2,out, dc_float_multiply,KL1B_B_FLOAT_MULTIPLY);
}


/*************************************************************************
*   b_float_divide(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_divide()
{
    DEF3D(blt_b_float_divide);
}

blt_b_float_divide(in1, in2, out)
    CELL *in1, *in2, *out;
{
    DEF3B(float_divide, in1, in2, out, dc_float_divide, KL1B_B_FLOAT_DIVIDE);
}


/*************************************************************************
*   b_float_minus(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_minus()
{
    DEF2D(blt_b_float_minus);
}

blt_b_float_minus(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2BN(float_minus, in, out, dc_float_minus, KL1B_B_FLOAT_MINUS);
}


/*************************************************************************
*   b_float_abs(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_abs()
{
    DEF2D(blt_b_float_abs);
}

blt_b_float_abs(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2BN(float_abs, in, out, dc_float_abs, KL1B_B_FLOAT_ABS);
}


/*************************************************************************
*   b_float_min(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_min()
{
    DEF3D(blt_b_float_min);
}

blt_b_float_min(in1, in2, out)
    CELL *in1, *in2, *out;
{
    DEF3BN(float_min, in1, in2, out, dc_float_min, KL1B_B_FLOAT_MIN);
}


/*************************************************************************
*   b_float_max(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_max()
{
    DEF3D(blt_b_float_max);
}

blt_b_float_max(in1, in2, out)
    CELL *in1, *in2, *out;
{
    DEF3BN(float_max, in1, in2, out, dc_float_max, KL1B_B_FLOAT_MAX);
}


/*************************************************************************
*   b_float_floor(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_floor()
{
    DEF2D(blt_b_float_floor);
}

blt_b_float_floor(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_floor, in, out, dc_float_floor, KL1B_B_FLOAT_FLOOR);
}


/*************************************************************************
*   b_float_sqrt(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_sqrt()
{
    DEF2D(blt_b_float_sqrt);
}

blt_b_float_sqrt(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_sqrt, in, out, dc_float_sqrt, KL1B_B_FLOAT_SQRT);
}


/*************************************************************************
*   b_float_ln(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_ln()
{
    DEF2D(blt_b_float_ln);
}

blt_b_float_ln(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_ln, in, out, dc_float_ln, KL1B_B_FLOAT_LN);
}


/*************************************************************************
*   b_float_log(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_log()
{
    DEF2D(blt_b_float_log);
}

blt_b_float_log(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_log, in, out, dc_float_log, KL1B_B_FLOAT_LOG);
}


/*************************************************************************
*   b_float_exp(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_exp()
{
    DEF2D(blt_b_float_exp);
}

blt_b_float_exp(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_exp, in, out, dc_float_exp, KL1B_B_FLOAT_EXP);
}


/*************************************************************************
*   b_float_pow(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_pow()
{
    DEF3D(blt_b_float_pow);
}

blt_b_float_pow(in1, in2, out)
    CELL *in1, *in2, *out;
{
    DEF3B(float_pow, in1, in2, out, dc_float_pow, KL1B_B_FLOAT_POW);
}


/*************************************************************************
*   b_float_sin(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_sin()
{
    DEF2D(blt_b_float_sin);
}

blt_b_float_sin(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_sin, in, out, dc_float_sin, KL1B_B_FLOAT_SIN);
}


/*************************************************************************
*   b_float_cos(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_cos()
{
    DEF2D(blt_b_float_cos);
}

blt_b_float_cos(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_cos, in, out, dc_float_cos, KL1B_B_FLOAT_COS);
}


/*************************************************************************
*   b_float_tan(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_tan()
{
    DEF2D(blt_b_float_tan);
}

blt_b_float_tan(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_tan, in, out, dc_float_tan, KL1B_B_FLOAT_TAN);
}


/*************************************************************************
*   b_float_asin(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_asin()
{
    DEF2D(blt_b_float_asin);
}

blt_b_float_asin(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_asin, in, out, dc_float_asin, KL1B_B_FLOAT_ASIN);
}


/*************************************************************************
*   b_float_acos(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_acos()
{
    DEF2D(blt_b_float_acos);
}

blt_b_float_acos(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_acos, in, out, dc_float_acos, KL1B_B_FLOAT_ACOS);
}


/*************************************************************************
*   b_float_atan(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_atan()
{
    DEF2D(blt_b_float_atan);
}

blt_b_float_atan(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_atan, in, out, dc_float_atan, KL1B_B_FLOAT_ATAN);
}


/*************************************************************************
*   b_float_atan2(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_atan2()
{
    DEF3D(blt_b_float_atan2);
}

blt_b_float_atan2(in1, in2, out)
    CELL *in1, *in2, *out;
{
    DEF3B(float_atan2, in1, in2, out, dc_float_atan2, KL1B_B_FLOAT_ATAN2);
}


/*************************************************************************
*   b_float_sinh(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_sinh()
{
    DEF2D(blt_b_float_sinh);
}

blt_b_float_sinh(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_sinh, in, out, dc_float_sinh, KL1B_B_FLOAT_SINH);
}


/*************************************************************************
*   b_float_cosh(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_cosh()
{
    DEF2D(blt_b_float_cosh);
}

blt_b_float_cosh(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_cosh, in, out, dc_float_cosh, KL1B_B_FLOAT_COSH);
}


/*************************************************************************
*   b_float_tanh(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_tanh()
{
    DEF2D(blt_b_float_tanh);
}

blt_b_float_tanh(in, out)
    register CELL *in;
    CELL *out;
{
    DEF2B(float_tanh, in, out, dc_float_tanh, KL1B_B_FLOAT_TANH);
}


/*************************************************************************
*   b_float_to_integer(Rin,^Rout)					 *
*************************************************************************/

DCODE dc_float_to_integer()
{
    blt_b_float_to_integer(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_float_to_integer(in, out)
    register CELL *in;
    CELL *out;
{
    Dereference(in);
    if(Typeof(in) != FLOAT){
	if(IsRef(in)){
	    body_builtin_suspend(dc_float_to_integer, in, IO, in, out);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_FLOAT_TO_INTEGER, IO, in, out);
	}
    }else{
	int *z;
	if(float_to_integer(&Valueof(in), &z)){
	    SetAll(out, INT, z, MRBOFF);
	}else{
	    body_builtin_exception(INTEGER_OVERFLOW, 0,
				   KL1B_B_FLOAT_TO_INTEGER, IO, in, out);
	}
    }
}


/*************************************************************************
*   b_integer_to_float(Rin,^Rout)					 *
*************************************************************************/

DCODE dc_integer_to_float()
{
    blt_b_integer_to_float(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_integer_to_float(in, out)
    register CELL *in;
    CELL *out;
{
    Dereference(in);
    if(Typeof(in) != INT){
	if(IsRef(in)){
	    body_builtin_suspend(dc_integer_to_float, in, IO, in, out);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_INTEGER_TO_FLOAT, IO, in, out);
	}
    }else{
	int *z;
	integer_to_float(&Valueof(in), &z);
	SetAll(out, FLOAT, z, MRBOFF);
    }
}
