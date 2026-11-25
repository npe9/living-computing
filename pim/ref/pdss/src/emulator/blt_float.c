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

int blt_g_float_add(CELL *in1, CELL *in2, CELL *out)
{
    int32_t z;
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

int blt_g_float_subtract(CELL *in1, CELL *in2, CELL *out)
{
    int32_t z;
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

int blt_g_float_multiply(CELL *in1, CELL *in2, CELL *out)
{
    int32_t z;
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

int blt_g_float_divide(CELL *in1, CELL *in2, CELL *out)
{
    int32_t z;
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

int blt_g_float_minus(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_abs(CELL *in, CELL *out)
{
    int32_t z;
    float_abs(&Valueof(in), &z);
    SetAll(out, FLOAT, z, MRBOFF);
    return(YES);
}


/*************************************************************************
*   g_float_min(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_min(CELL *in1, CELL *in2, CELL *out)
{
    int32_t z;
    float_min(&Valueof(in1), &Valueof(in2), &z);
    SetAll(out, FLOAT, z, MRBOFF);
    return(YES);
}


/*************************************************************************
*   g_float_max(Rin1,Rin2,^Rout)					 *
*************************************************************************/

int blt_g_float_max(CELL *in1, CELL *in2, CELL *out)
{
    int32_t z;
    float_max(&Valueof(in1), &Valueof(in2), &z);
    SetAll(out, FLOAT, z, MRBOFF);
    return(YES);
}


/*************************************************************************
*   g_float_floor(Rin,^Rout)						 *
*************************************************************************/

int blt_g_float_floor(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_sqrt(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_ln(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_log(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_exp(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_pow(CELL *in1, CELL *in2, CELL *out)
{
    int32_t z;
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

int blt_g_float_sin(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_cos(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_tan(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_asin(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_acos(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_atan(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_atan2(CELL *in1, CELL *in2, CELL *out)
{
    int32_t z;
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

int blt_g_float_sinh(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_cosh(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_tanh(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_float_to_integer(CELL *in, CELL *out)
{
    int32_t z;
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

int blt_g_integer_to_float(CELL *in, CELL *out)
{
    int32_t z;
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
	    body_builtin_suspend(CodeOfFunction(DC), x, IIO, IN1, IN2, OUT);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==IN1 ? 1 : 2),\
				   OP, IIO, IN1, IN2, OUT);\
	}\
    }else{\
	int32_t z;\
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
	    body_builtin_suspend(CodeOfFunction(DC), x, IIO, IN1, IN2, OUT);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==IN1 ? 1 : 2),\
				   OP, IIO, IN1, IN2, OUT);\
	}\
    }else{\
	int32_t z;\
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
	    body_builtin_suspend(CodeOfFunction(DC), IN, IO, IN, OUT);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1, OP, IO, IN, OUT);\
	}\
    }else{\
	int32_t z;\
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
	    body_builtin_suspend(CodeOfFunction(DC), IN, IO, IN, OUT);\
	}else{\
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1, OP, IO, IN, OUT);\
	}\
    }else{\
	int32_t z;\
	FN(&Valueof(IN), &z);\
	SetAll(OUT, FLOAT, z, MRBOFF);\
    }\
}


/*************************************************************************
*   b_float_add(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_add(void)
{
    DEF3D(blt_b_float_add);
}

int blt_b_float_add(CELL *in1, CELL *in2, CELL *out)
{
    DEF3B(float_add, in1, in2, out, dc_float_add, KL1B_B_FLOAT_ADD);
    return 0;
}


/*************************************************************************
*   b_float_subtract(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_subtract(void)
{
    DEF3D(blt_b_float_subtract);
}

int blt_b_float_subtract(CELL *in1, CELL *in2, CELL *out)
{
    DEF3B(float_subtract,in1,in2,out, dc_float_subtract,KL1B_B_FLOAT_SUBTRACT);
    return 0;
}


/*************************************************************************
*   b_float_multiply(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_multiply(void)
{
    DEF3D(blt_b_float_multiply);
}

int blt_b_float_multiply(CELL *in1, CELL *in2, CELL *out)
{
    DEF3B(float_multiply,in1,in2,out, dc_float_multiply,KL1B_B_FLOAT_MULTIPLY);
    return 0;
}


/*************************************************************************
*   b_float_divide(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_divide(void)
{
    DEF3D(blt_b_float_divide);
}

int blt_b_float_divide(CELL *in1, CELL *in2, CELL *out)
{
    DEF3B(float_divide, in1, in2, out, dc_float_divide, KL1B_B_FLOAT_DIVIDE);
    return 0;
}


/*************************************************************************
*   b_float_minus(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_minus(void)
{
    DEF2D(blt_b_float_minus);
}

int blt_b_float_minus(register CELL *in, CELL *out)
{
    DEF2BN(float_minus, in, out, dc_float_minus, KL1B_B_FLOAT_MINUS);
    return 0;
}


/*************************************************************************
*   b_float_abs(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_abs(void)
{
    DEF2D(blt_b_float_abs);
}

int blt_b_float_abs(register CELL *in, CELL *out)
{
    DEF2BN(float_abs, in, out, dc_float_abs, KL1B_B_FLOAT_ABS);
    return 0;
}


/*************************************************************************
*   b_float_min(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_min(void)
{
    DEF3D(blt_b_float_min);
}

int blt_b_float_min(CELL *in1, CELL *in2, CELL *out)
{
    DEF3BN(float_min, in1, in2, out, dc_float_min, KL1B_B_FLOAT_MIN);
    return 0;
}


/*************************************************************************
*   b_float_max(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_max(void)
{
    DEF3D(blt_b_float_max);
}

int blt_b_float_max(CELL *in1, CELL *in2, CELL *out)
{
    DEF3BN(float_max, in1, in2, out, dc_float_max, KL1B_B_FLOAT_MAX);
    return 0;
}


/*************************************************************************
*   b_float_floor(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_floor(void)
{
    DEF2D(blt_b_float_floor);
}

int blt_b_float_floor(register CELL *in, CELL *out)
{
    DEF2B(float_floor, in, out, dc_float_floor, KL1B_B_FLOAT_FLOOR);
    return 0;
}


/*************************************************************************
*   b_float_sqrt(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_sqrt(void)
{
    DEF2D(blt_b_float_sqrt);
}

int blt_b_float_sqrt(register CELL *in, CELL *out)
{
    DEF2B(float_sqrt, in, out, dc_float_sqrt, KL1B_B_FLOAT_SQRT);
    return 0;
}


/*************************************************************************
*   b_float_ln(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_ln(void)
{
    DEF2D(blt_b_float_ln);
}

int blt_b_float_ln(register CELL *in, CELL *out)
{
    DEF2B(float_ln, in, out, dc_float_ln, KL1B_B_FLOAT_LN);
    return 0;
}


/*************************************************************************
*   b_float_log(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_log(void)
{
    DEF2D(blt_b_float_log);
}

int blt_b_float_log(register CELL *in, CELL *out)
{
    DEF2B(float_log, in, out, dc_float_log, KL1B_B_FLOAT_LOG);
    return 0;
}


/*************************************************************************
*   b_float_exp(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_exp(void)
{
    DEF2D(blt_b_float_exp);
}

int blt_b_float_exp(register CELL *in, CELL *out)
{
    DEF2B(float_exp, in, out, dc_float_exp, KL1B_B_FLOAT_EXP);
    return 0;
}


/*************************************************************************
*   b_float_pow(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_pow(void)
{
    DEF3D(blt_b_float_pow);
}

int blt_b_float_pow(CELL *in1, CELL *in2, CELL *out)
{
    DEF3B(float_pow, in1, in2, out, dc_float_pow, KL1B_B_FLOAT_POW);
    return 0;
}


/*************************************************************************
*   b_float_sin(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_sin(void)
{
    DEF2D(blt_b_float_sin);
}

int blt_b_float_sin(register CELL *in, CELL *out)
{
    DEF2B(float_sin, in, out, dc_float_sin, KL1B_B_FLOAT_SIN);
    return 0;
}


/*************************************************************************
*   b_float_cos(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_cos(void)
{
    DEF2D(blt_b_float_cos);
}

int blt_b_float_cos(register CELL *in, CELL *out)
{
    DEF2B(float_cos, in, out, dc_float_cos, KL1B_B_FLOAT_COS);
    return 0;
}


/*************************************************************************
*   b_float_tan(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_tan(void)
{
    DEF2D(blt_b_float_tan);
}

int blt_b_float_tan(register CELL *in, CELL *out)
{
    DEF2B(float_tan, in, out, dc_float_tan, KL1B_B_FLOAT_TAN);
    return 0;
}


/*************************************************************************
*   b_float_asin(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_asin(void)
{
    DEF2D(blt_b_float_asin);
}

int blt_b_float_asin(register CELL *in, CELL *out)
{
    DEF2B(float_asin, in, out, dc_float_asin, KL1B_B_FLOAT_ASIN);
    return 0;
}


/*************************************************************************
*   b_float_acos(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_acos(void)
{
    DEF2D(blt_b_float_acos);
}

int blt_b_float_acos(register CELL *in, CELL *out)
{
    DEF2B(float_acos, in, out, dc_float_acos, KL1B_B_FLOAT_ACOS);
    return 0;
}


/*************************************************************************
*   b_float_atan(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_atan(void)
{
    DEF2D(blt_b_float_atan);
}

int blt_b_float_atan(register CELL *in, CELL *out)
{
    DEF2B(float_atan, in, out, dc_float_atan, KL1B_B_FLOAT_ATAN);
    return 0;
}


/*************************************************************************
*   b_float_atan2(Rin1,Rin2,^Rout)					 *
*************************************************************************/

DCODE dc_float_atan2(void)
{
    DEF3D(blt_b_float_atan2);
}

int blt_b_float_atan2(CELL *in1, CELL *in2, CELL *out)
{
    DEF3B(float_atan2, in1, in2, out, dc_float_atan2, KL1B_B_FLOAT_ATAN2);
    return 0;
}


/*************************************************************************
*   b_float_sinh(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_sinh(void)
{
    DEF2D(blt_b_float_sinh);
}

int blt_b_float_sinh(register CELL *in, CELL *out)
{
    DEF2B(float_sinh, in, out, dc_float_sinh, KL1B_B_FLOAT_SINH);
    return 0;
}


/*************************************************************************
*   b_float_cosh(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_cosh(void)
{
    DEF2D(blt_b_float_cosh);
}

int blt_b_float_cosh(register CELL *in, CELL *out)
{
    DEF2B(float_cosh, in, out, dc_float_cosh, KL1B_B_FLOAT_COSH);
    return 0;
}


/*************************************************************************
*   b_float_tanh(Rin,^Rout)						 *
*************************************************************************/

DCODE dc_float_tanh(void)
{
    DEF2D(blt_b_float_tanh);
}

int blt_b_float_tanh(register CELL *in, CELL *out)
{
    DEF2B(float_tanh, in, out, dc_float_tanh, KL1B_B_FLOAT_TANH);
    return 0;
}


/*************************************************************************
*   b_float_to_integer(Rin,^Rout)					 *
*************************************************************************/

DCODE dc_float_to_integer(void)
{
    blt_b_float_to_integer(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_float_to_integer(register CELL *in, CELL *out)
{
    Dereference(in);
    if(Typeof(in) != FLOAT){
	if(IsRef(in)){
	    body_builtin_suspend(CodeOfFunction(dc_float_to_integer), in, IO, in, out);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_FLOAT_TO_INTEGER, IO, in, out);
	}
    }else{
	int32_t z;
	if(float_to_integer(&Valueof(in), &z)){
	    SetAll(out, INT, z, MRBOFF);
	}else{
	    body_builtin_exception(INTEGER_OVERFLOW, 0,
				   KL1B_B_FLOAT_TO_INTEGER, IO, in, out);
	}
    }
    return 0;
}


/*************************************************************************
*   b_integer_to_float(Rin,^Rout)					 *
*************************************************************************/

DCODE dc_integer_to_float(void)
{
    blt_b_integer_to_float(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_integer_to_float(register CELL *in, CELL *out)
{
    Dereference(in);
    if(Typeof(in) != INT){
	if(IsRef(in)){
	    body_builtin_suspend(CodeOfFunction(dc_integer_to_float), in, IO, in, out);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_INTEGER_TO_FLOAT, IO, in, out);
	}
    }else{
	int32_t z;
	integer_to_float(&Valueof(in), &z);
	SetAll(out, FLOAT, z, MRBOFF);
    }
    return 0;
}
