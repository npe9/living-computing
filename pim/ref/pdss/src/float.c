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

initialize_float_calculator()
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

int float_equal(x, y)	       float *x, *y;  { return(*x == *y); }
int float_not_equal(x, y)      float *x, *y;  { return(*x != *y); }
int float_less_than(x, y)      float *x, *y;  { return(*x <  *y); }
int float_not_less_than(x, y)  float *x, *y;  { return(*x >= *y); }


/*************************************************************************
*   Calculate Floating Point Number.					 *
*************************************************************************/

int float_add(x, y, z)	     float *x, *y, *z;	{ CALC(*x + *y);	    }
int float_subtract(x, y, z)  float *x, *y, *z;	{ CALC(*x - *y);	    }
int float_multiply(x, y, z)  float *x, *y, *z;	{ CALC(*x * *y);	    }
int float_divide(x, y, z)    float *x, *y, *z;	{ CALC(*x / *y);	    }
    float_minus(x, z)	     float *x, *z;	{ *z = -(*x);		    }
    float_abs(x, z)	     float *x, *z;	{ *z = *x < 0 ? -(*x) : *x; }
    float_min(x, y, z)	     float *x, *y, *z;	{ *z = *x < *y ? *x : *y;   }
    float_max(x, y, z)	     float *x, *y, *z;	{ *z = *x > *y ? *x : *y;   }
int float_floor(x, z)	     float *x, *z;	{ CALC(floor(*x));	    }
int float_sqrt(x, z)	     float *x, *z;	{ CALC(sqrt(*x));	    }
int float_ln(x, z)	     float *x, *z;	{ CALC(log(*x));	    }
int float_log(x, z)	     float *x, *z;	{ CALC(log10(*x));	    }
int float_exp(x, z)	     float *x, *z;	{ CALC(exp(*x));	    }
int float_pow(x, y, z)	     float *x, *y, *z;	{ CALC(pow(*x, *y));	    }
int float_sin(x, z)	     float *x, *z;	{ CALC(sin(*x));	    }
int float_cos(x, z)	     float *x, *z;	{ CALC(cos(*x));	    }
int float_tan(x, z)	     float *x, *z;	{ CALC(tan(*x));	    }
int float_asin(x, z)	     float *x, *z;	{ CALC(asin(*x));	    }
int float_acos(x, z)	     float *x, *z;	{ CALC(acos(*x));	    }
int float_atan(x, z)	     float *x, *z;	{ CALC(atan(*x));	    }
int float_atan2(x, y, z)     float *x, *y, *z;	{ CALC(atan2(*x, *y));	    }
int float_sinh(x, z)	     float *x, *z;	{ CALC(sinh(*x));	    }
int float_cosh(x, z)	     float *x, *z;	{ CALC(cosh(*x));	    }
int float_tanh(x, z)	     float *x, *z;	{ CALC(tanh(*x));	    }


/*************************************************************************
*   Convert Floating Point <-> Integer.					 *
*************************************************************************/

int float_to_integer(x, y)
    float *x;
    int *y;
{
#if !IGNORE_INTEGER_OVERFLOW
    if(IntOverflow(*x)) return(NO);
#endif
    *y = *x;
    return(YES);
}

integer_to_float(x, y)
    float *y;
    int *x;
{
    *y = *x;
}


/*************************************************************************
*   Convert Floating to String.						 *
*************************************************************************/

CHAR *float_to_string(x)
    float *x;
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

int string_to_float(s, z)
    register CHAR *s;
    float *z;
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
