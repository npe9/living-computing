/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include <math.h>
#include <stdlib.h>	/* atof() returns double: undeclared, it was taken as int */
#include <signal.h>
#include <errno.h>
#include "pdss.h"

static float_error() { errno = -1; }

int initialize_float_calculator(void)
{
    signal(SIGFPE, float_error);
}

#define FLOAT_HUGE 3.4028234e38

#define CALC(EXP){\
    double work;\
    errno = 0;\
    work = EXP;\
    if(!errno && work >= -FLOAT_HUGE && work <= FLOAT_HUGE){\
	*z = work;\
	return(YES);\
    }else{\
	return(NO);\
    }\
}


/*************************************************************************
*   Compare Floating Point Number.					 *
*************************************************************************/

int float_equal(float *x, float *y)  { return(*x == *y); }
int float_not_equal(float *x, float *y)  { return(*x != *y); }
int float_less_than(float *x, float *y)  { return(*x <  *y); }
int float_not_less_than(float *x, float *y)  { return(*x >= *y); }


/*************************************************************************
*   Calculate Floating Point Number.					 *
*************************************************************************/

/* MODERN: float_minus/abs/min/max had no return statement, and their
   callers test the result, which was whatever the register held (YES in
   practice: test/b_f_func*.kl1 pass).  They now return YES. */

int float_add(float *x, float *y, float *z)	{ CALC(*x + *y);	    }
int float_subtract(float *x, float *y, float *z)	{ CALC(*x - *y);	    }
int float_multiply(float *x, float *y, float *z)	{ CALC(*x * *y);	    }
int float_divide(float *x, float *y, float *z)	{ CALC(*x / *y);	    }
int float_minus(float *x, float *z)	{ *z = -(*x); return(YES); }
int float_abs(float *x, float *z)	{ *z = *x < 0 ? -(*x) : *x; return(YES); }
int float_min(float *x, float *y, float *z)	{ *z = *x < *y ? *x : *y; return(YES); }
int float_max(float *x, float *y, float *z)	{ *z = *x > *y ? *x : *y; return(YES); }
int float_floor(float *x, float *z)	{ CALC(floor(*x));	    }
int float_sqrt(float *x, float *z)	{ CALC(sqrt(*x));	    }
int float_ln(float *x, float *z)	{ CALC(log(*x));	    }
int float_log(float *x, float *z)	{ CALC(log10(*x));	    }
int float_exp(float *x, float *z)	{ CALC(exp(*x));	    }
int float_pow(float *x, float *y, float *z)	{ CALC(pow(*x, *y));	    }
int float_sin(float *x, float *z)	{ CALC(sin(*x));	    }
int float_cos(float *x, float *z)	{ CALC(cos(*x));	    }
int float_tan(float *x, float *z)	{ CALC(tan(*x));	    }
int float_asin(float *x, float *z)	{ CALC(asin(*x));	    }
int float_acos(float *x, float *z)	{ CALC(acos(*x));	    }
int float_atan(float *x, float *z)	{ CALC(atan(*x));	    }
int float_atan2(float *x, float *y, float *z)	{ CALC(atan2(*x, *y));	    }
int float_sinh(float *x, float *z)	{ CALC(sinh(*x));	    }
int float_cosh(float *x, float *z)	{ CALC(cosh(*x));	    }
int float_tanh(float *x, float *z)	{ CALC(tanh(*x));	    }


/*************************************************************************
*   Convert Floating Point <-> Integer.					 *
*************************************************************************/

int float_to_integer(float *x, int *y)
{
#if !IGNORE_INTEGER_OVERFLOW
    if(IntOverflow(*x)) return(NO);
#endif
    *y = *x;
    return(YES);
}

int integer_to_float(int *x, float *y)
{
    *y = *x;
}


/*************************************************************************
*   Convert Floating to String.						 *
*************************************************************************/

CHAR *float_to_string(float *x)
{
    register CHAR *p, *q, *b;
    static CHAR buf[32];
    b = buf+1;
    sprintf(b, "%g", *x);
    if(*b == '.'){
	*--b = '0';
    }
    for(p = b; *p; p++){
	if(*p == '.'){
	    return(b);
	}
	if(*p == 'e'){
	    for(q = p; *q; q++);
	    while(q >= p){ q[2] = q[0]; q--; }
	    p[0] = '.';
	    p[1] = '0';
	    return(b);
	}
    }
    p[0] = '.';
    p[1] = '0';
    p[2] = 0;
    return(b);
}


/*************************************************************************
*   Convert String to Floating.						 *
*************************************************************************/

int string_to_float(register CHAR *s, float *z)
{
    double work;
    errno = 0;
    work = atof(s);
#ifdef SYMMETRY
    atof("0");	/** Dummy, for BUG? of library on Symmetry **/
#endif
    if(!errno && work >= -FLOAT_HUGE && work <= FLOAT_HUGE){
	*z = work;
	return(YES);
    }else{
	*z = 0.0;
	return(NO);
    }
}
