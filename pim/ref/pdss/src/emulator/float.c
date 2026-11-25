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

static void float_error(int sig) { (void)sig; errno = -1; }

int initialize_float_calculator(void)
{
    signal(SIGFPE, float_error);
    return(YES);
}

#define FLOAT_HUGE 3.4028234e38

/* MODERN: a float lives in a cell's 32-bit value; these functions take a
   pointer to that value (int32_t, as the callers always passed an int)
   and read or write it as a float with memcpy (port.h), not through a
   float pointer to an int. */
#define F(p)	pdss_float_of(p)
#define SF(p,v)	pdss_set_float((p), (float)(v))

#define CALC(EXP){\
    double work;\
    errno = 0;\
    work = EXP;\
    if(!errno && work >= -FLOAT_HUGE && work <= FLOAT_HUGE){\
	SF(z, work);\
	return(YES);\
    }else{\
	return(NO);\
    }\
}


/*************************************************************************
*   Compare Floating Point Number.					 *
*************************************************************************/

int float_equal(int32_t *x, int32_t *y)  { return(F(x) == F(y)); }
int float_not_equal(int32_t *x, int32_t *y)  { return(F(x) != F(y)); }
int float_less_than(int32_t *x, int32_t *y)  { return(F(x) <  F(y)); }
int float_not_less_than(int32_t *x, int32_t *y)  { return(F(x) >= F(y)); }


/*************************************************************************
*   Calculate Floating Point Number.					 *
*************************************************************************/

/* MODERN: float_minus/abs/min/max had no return statement, and their
   callers test the result, which was whatever the register held (YES in
   practice: test/b_f_func*.kl1 pass).  They now return YES. */

int float_add(int32_t *x, int32_t *y, int32_t *z)	{ CALC(F(x) + F(y));	    }
int float_subtract(int32_t *x, int32_t *y, int32_t *z)	{ CALC(F(x) - F(y));	    }
int float_multiply(int32_t *x, int32_t *y, int32_t *z)	{ CALC(F(x) * F(y));	    }
int float_divide(int32_t *x, int32_t *y, int32_t *z)	{ CALC(F(x) / F(y));	    }
int float_minus(int32_t *x, int32_t *z)	{ SF(z, -F(x)); return(YES); }
int float_abs(int32_t *x, int32_t *z)	{ SF(z, F(x) < 0 ? -F(x) : F(x)); return(YES); }
int float_min(int32_t *x, int32_t *y, int32_t *z)	{ SF(z, F(x) < F(y) ? F(x) : F(y)); return(YES); }
int float_max(int32_t *x, int32_t *y, int32_t *z)	{ SF(z, F(x) > F(y) ? F(x) : F(y)); return(YES); }
int float_floor(int32_t *x, int32_t *z)	{ CALC(floor(F(x)));	    }
int float_sqrt(int32_t *x, int32_t *z)	{ CALC(sqrt(F(x)));	    }
int float_ln(int32_t *x, int32_t *z)	{ CALC(log(F(x)));	    }
int float_log(int32_t *x, int32_t *z)	{ CALC(log10(F(x)));	    }
int float_exp(int32_t *x, int32_t *z)	{ CALC(exp(F(x)));	    }
int float_pow(int32_t *x, int32_t *y, int32_t *z)	{ CALC(pow(F(x), F(y)));	    }
int float_sin(int32_t *x, int32_t *z)	{ CALC(sin(F(x)));	    }
int float_cos(int32_t *x, int32_t *z)	{ CALC(cos(F(x)));	    }
int float_tan(int32_t *x, int32_t *z)	{ CALC(tan(F(x)));	    }
int float_asin(int32_t *x, int32_t *z)	{ CALC(asin(F(x)));	    }
int float_acos(int32_t *x, int32_t *z)	{ CALC(acos(F(x)));	    }
int float_atan(int32_t *x, int32_t *z)	{ CALC(atan(F(x)));	    }
int float_atan2(int32_t *x, int32_t *y, int32_t *z)	{ CALC(atan2(F(x), F(y)));	    }
int float_sinh(int32_t *x, int32_t *z)	{ CALC(sinh(F(x)));	    }
int float_cosh(int32_t *x, int32_t *z)	{ CALC(cosh(F(x)));	    }
int float_tanh(int32_t *x, int32_t *z)	{ CALC(tanh(F(x)));	    }


/*************************************************************************
*   Convert Floating Point <-> Integer.					 *
*************************************************************************/

int float_to_integer(int32_t *x, int32_t *y)
{
#if !IGNORE_INTEGER_OVERFLOW
    if(IntOverflow(F(x))) return(NO);
#endif
    *y = (int32_t)F(x);
    return(YES);
}

int integer_to_float(int32_t *x, int32_t *y)
{
    SF(y, *x);
    return(YES);
}


/*************************************************************************
*   Convert Floating to String.						 *
*************************************************************************/

CHAR *float_to_string(int32_t *x)
{
    register CHAR *p, *q, *b;
    static CHAR buf[32];
    b = buf+1;
    sprintf(b, "%g", F(x));
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

int string_to_float(register CHAR *s, int32_t *z)
{
    double work;
    errno = 0;
    work = atof(s);
#ifdef SYMMETRY
    atof("0");	/** Dummy, for BUG? of library on Symmetry **/
#endif
    if(!errno && work >= -FLOAT_HUGE && work <= FLOAT_HUGE){
	SF(z, work);
	return(YES);
    }else{
	SF(z, 0.0);
	return(NO);
    }
}
