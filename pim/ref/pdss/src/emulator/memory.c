/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"

CHAR *mesg_heap_area_overflow = (CHAR *)"Heap Area Overflow.";
CHAR *mesg_code_area_overflow = (CHAR *)"Code Area Overflow.";


/*************************************************************************
*   Heap Area Management.						 *
*************************************************************************/

int  heap_size;
CELL *H;
CELL *heap1=NULL, *heap1_warn, *heap1_limit; /* Current Set */
CELL *heap2=NULL, *heap2_warn, *heap2_limit; /* Another Set */

#if MRBGC_SWITCH && MRBGC_FREE_LIST_TYPE==0
CELL *f01top,  *f02top,	 *f03top,  *f04top,  *f05top;
CELL *f06top,  *f07top,	 *f08top,  *f16top,  *f32top;
#if MRBGC_STATISTICS
int  f01peek,  f02peek,	 f03peek,  f04peek,  f05peek;
int  f06peek,  f07peek,	 f08peek,  f16peek,  f32peek,  f99peek;
int  f01total, f02total, f03total, f04total, f05total;
int  f06total, f07total, f08total, f16total, f32total, f99total;
int  f01used,  f02used,	 f03used,  f04used,  f05used;
int  f06used,  f07used,	 f08used,  f16used,  f32used,  f99used;
#if MRBGC_STATISTICS == 2
int  mst_deref;
int  mst_cslst, mst_cflst;
int  mst_csv01, mst_csv02, mst_csv03, mst_csv04, mst_csv05;
int  mst_csv06, mst_csv07, mst_csv08, mst_csv16, mst_csv32;
int  mst_cfv01, mst_cfv02, mst_cfv03, mst_cfv04, mst_cfv05;
int  mst_cfv06, mst_cfv07, mst_cfv08, mst_cfv16, mst_cfv32;
int  mst_cvl01, mst_cvl02, mst_cvl03, mst_cvl04, mst_cvl05;
int  mst_cvl06, mst_cvl07, mst_cvl08, mst_cvl16, mst_cvl32;
int  mst_cbl01, mst_cbl02, mst_cbl03, mst_cbl04, mst_cbl05;
int  mst_cbl06, mst_cbl07, mst_cbl08, mst_cbl16, mst_cbl32;
int  mst_rslst, mst_rflst;
int  mst_rsv01, mst_rsv02, mst_rsv03, mst_rsv04, mst_rsv05;
int  mst_rsv06, mst_rsv07, mst_rsv08, mst_rsv16, mst_rsv32, mst_rsv99;
int  mst_rfv01, mst_rfv02, mst_rfv03, mst_rfv04, mst_rfv05;
int  mst_rfv06, mst_rfv07, mst_rfv08, mst_rfv16, mst_rfv32, mst_rfv99;
int  mst_rbl01, mst_rbl02, mst_rbl03, mst_rbl04, mst_rbl05;
int  mst_rbl06, mst_rbl07, mst_rbl08, mst_rbl16, mst_rbl32, mst_rbl99;
int  mst_merge;
#endif
#endif
#endif
#if MRBGC_SWITCH && MRBGC_FREE_LIST_TYPE==1
CELL *f01top,  *f02top,	 *f04top,  *f08top;
CELL *f16top,  *f32top,	 *f64top,  *f28top;
#if MRBGC_STATISTICS
int  f01peek,  f02peek,	 f04peek,  f08peek;
int  f16peek,  f32peek,	 f64peek,  f28peek,  f99peek;
int  f01total, f02total, f04total, f08total;
int  f16total, f32total, f64total, f28total, f99total;
int  f01used,  f02used,	 f04used,  f08used;
int  f16used,  f32used,	 f64used,  f28used,  f99used;
#if MRBGC_STATISTICS == 2
int  mst_deref;
int  mst_cslst, mst_cflst;
int  mst_csv01, mst_csv02, mst_csv04, mst_csv08;
int  mst_csv16, mst_csv32, mst_csv64, mst_csv28;
int  mst_cfv01, mst_cfv02, mst_cfv04, mst_cfv08;
int  mst_cfv16, mst_cfv32, mst_cfv64, mst_cfv28;
int  mst_cvl01, mst_cvl02, mst_cvl04, mst_cvl08;
int  mst_cvl16, mst_cvl32, mst_cvl64, mst_cvl28;
int  mst_cbl01, mst_cbl02, mst_cbl04, mst_cbl08;
int  mst_cbl16, mst_cbl32, mst_cbl64, mst_cbl28;
int  mst_rslst, mst_rflst;
int  mst_rsv01, mst_rsv02, mst_rsv04, mst_rsv08;
int  mst_rsv16, mst_rsv32, mst_rsv64, mst_rsv28, mst_rsv99;
int  mst_rfv01, mst_rfv02, mst_rfv04, mst_rfv08;
int  mst_rfv16, mst_rfv32, mst_rfv64, mst_rfv28, mst_rfv99;
int  mst_rbl01, mst_rbl02, mst_rbl04, mst_rbl08;
int  mst_rbl16, mst_rbl32, mst_rbl64, mst_rbl28, mst_rbl99;
int  mst_merge;
#endif
#endif
#endif

SUSPENSION_RECORD *srec_pool_top;
int srec_peek;
#if MRBGC_STATISTICS
int srec_total, srec_used;
#endif

GOAL_RECORD   *grec08_pool_top;
GOAL_RECORD16 *grec16_pool_top;
GOAL_RECORD32 *grec32_pool_top;
int grec08_peek,  grec16_peek,	grec32_peek;
#if MRBGC_STATISTICS
int grec08_total, grec16_total, grec32_total;
int grec08_used,  grec16_used,	grec32_used;
#endif
GOAL_RECORD *goal_rec_list;	    /* for Deadlock Detection */
GOAL_RECORD *goal_rec_list_old;	    /* for Deadlock Detection */
MERGER_RECORD *merger_rec_list;	    /* for Deadlock Detection */
MERGER_RECORD *merger_rec_list_old; /* for Deadlock Detection */

PARENT_RECORD *prec_pool_top;
int prec_peek;
#if MRBGC_STATISTICS
int prec_total, prec_used;
#endif

int initialize_heap(unsigned int size)
{
    heap_size = size;
    if(heap1 == NULL) heap1 = (CELL *)malloc(sizeof(CELL) * size);
    if(heap2 == NULL) heap2 = (CELL *)malloc(sizeof(CELL) * size);
    if(heap1 == NULL || heap2 == NULL){
	Error("Not Enough Memory (malloc failure, heap) -- Aborted.");
	exit_pdss(1);
    }
    H = heap1;
    heap1_limit = heap1+size;
    heap1_warn	= heap1_limit-size/100;
    heap2_limit = heap2+size;
    heap2_warn	= heap2_limit-size/100;
#if MRBGC_SWITCH && MRBGC_FREE_LIST_TYPE==0
    f01top = f02top = f03top = f04top = f05top = NULL;
    f06top = f07top = f08top = f16top = f32top = NULL;
#if MRBGC_STATISTICS
    f01peek  = f02peek	= f03peek  = f04peek  = f05peek	 = 0;
    f06peek  = f07peek	= f08peek  = f16peek  = f32peek	 = 0;
    f01total = f02total = f03total = f04total = f05total = 0;
    f06total = f07total = f08total = f16total = f32total = 0;
    f01used  = f02used	= f03used  = f04used  = f05used	 = 0;
    f06used  = f07used	= f08used  = f16used  = f32used	 = 0;
    f99peek  = f99total = f99used  = 0;
#if MRBGC_STATISTICS == 2
    mst_deref = 0;
    mst_cslst = mst_cflst = 0;
    mst_csv01 = mst_csv02 = mst_csv03 = mst_csv04 = mst_csv05 = 0;
    mst_csv06 = mst_csv07 = mst_csv08 = mst_csv16 = mst_csv32 = 0;
    mst_cfv01 = mst_cfv02 = mst_cfv03 = mst_cfv04 = mst_cfv05 = 0;
    mst_cfv06 = mst_cfv07 = mst_cfv08 = mst_cfv16 = mst_cfv32 = 0;
    mst_cvl01 = mst_cvl02 = mst_cvl03 = mst_cvl04 = mst_cvl05 = 0;
    mst_cvl06 = mst_cvl07 = mst_cvl08 = mst_cvl16 = mst_cvl32 = 0;
    mst_cbl01 = mst_cbl02 = mst_cbl03 = mst_cbl04 = mst_cbl05 = 0;
    mst_cbl06 = mst_cbl07 = mst_cbl08 = mst_cbl16 = mst_cbl32 = 0;
    mst_rslst = mst_rflst = 0;
    mst_rsv01 = mst_rsv02 = mst_rsv03 = mst_rsv04 = mst_rsv05 = 0;
    mst_rsv06 = mst_rsv07 = mst_rsv08 = mst_rsv16 = mst_rsv32 = 0;
    mst_rfv01 = mst_rfv02 = mst_rfv03 = mst_rfv04 = mst_rfv05 = 0;
    mst_rfv06 = mst_rfv07 = mst_rfv08 = mst_rfv16 = mst_rfv32 = 0;
    mst_rbl01 = mst_rbl02 = mst_rbl03 = mst_rbl04 = mst_rbl05 = 0;
    mst_rbl06 = mst_rbl07 = mst_rbl08 = mst_rbl16 = mst_rbl32 = 0;
    mst_rsv99 = mst_rfv99 = mst_rbl99 = 0;
    mst_merge = 0;
#endif
#endif
#endif
#if MRBGC_SWITCH && MRBGC_FREE_LIST_TYPE==1
    f01top = f02top = f04top = f08top = NULL;
    f16top = f32top = f64top = f28top = NULL;
#if MRBGC_STATISTICS
    f01peek  = f02peek	= f04peek  = f08peek  = 0;
    f16peek  = f32peek	= f64peek  = f28peek  = 0;
    f01total = f02total = f04total = f08total = 0;
    f16total = f32total = f64total = f28total = 0;
    f01used  = f02used	= f04used  = f08used  = 0;
    f16used  = f32used	= f64used  = f28used  = 0;
    f99peek  = f99total = f99used  = 0;
#if MRBGC_STATISTICS == 2
    mst_deref = 0;
    mst_cslst = mst_cflst = 0;
    mst_csv01 = mst_csv02 = mst_csv04 = mst_csv08 = 0;
    mst_csv16 = mst_csv32 = mst_csv64 = mst_csv28 = 0;
    mst_cfv01 = mst_cfv02 = mst_cfv04 = mst_cfv08 = 0;
    mst_cfv16 = mst_cfv32 = mst_cfv64 = mst_cfv28 = 0;
    mst_cvl01 = mst_cvl02 = mst_cvl04 = mst_cvl08 = 0;
    mst_cvl16 = mst_cvl32 = mst_cvl64 = mst_cvl28 = 0;
    mst_cbl01 = mst_cbl02 = mst_cbl04 = mst_cbl08 = 0;
    mst_cbl16 = mst_cbl32 = mst_cbl64 = mst_cbl28 = 0;
    mst_rslst = mst_rflst = 0;
    mst_rsv01 = mst_rsv02 = mst_rsv04 = mst_rsv08 = 0;
    mst_rsv16 = mst_rsv32 = mst_rsv64 = mst_rsv28 = 0;
    mst_rfv01 = mst_rfv02 = mst_rfv04 = mst_rfv08 = 0;
    mst_rfv16 = mst_rfv32 = mst_rfv64 = mst_rfv28 = 0;
    mst_rbl01 = mst_rbl02 = mst_rbl04 = mst_rbl08 = 0;
    mst_rbl16 = mst_rbl32 = mst_rbl64 = mst_rbl28 = 0;
    mst_rsv99 = mst_rfv99 = mst_rbl99 = 0;
    mst_merge = 0;
#endif
#endif
#endif
    srec_pool_top   = NULL; srec_peek	= 0;
    grec08_pool_top = NULL; grec08_peek = 0;
    grec16_pool_top = NULL; grec16_peek = 0;
    grec32_pool_top = NULL; grec32_peek = 0;
    prec_pool_top   = NULL; prec_peek	= 0;
#if MRBGC_STATISTICS
    srec_total	 = 0; srec_used	  = 0;
    grec08_total = 0; grec08_used = 0;
    grec16_total = 0; grec16_used = 0;
    grec32_total = 0; grec32_used = 0;
    prec_total	 = 0; prec_used	  = 0;
#endif
    goal_rec_list = goal_rec_list_old = NULL;
    merger_rec_list = merger_rec_list_old = NULL;
    t3_free();
    t4_free();
    gc_counter = 0;
    gc_panic_flag = 0;
    return 0;
}

int switch_heap(void)
{
    CELL *work;

    work = heap1;	heap1	    = heap2;	   heap2       = work;
    work = heap1_limit; heap1_limit = heap2_limit; heap2_limit = work;
    work = heap1_warn;	heap1_warn  = heap2_warn;  heap2_warn  = work;
    H = heap1;
#if MRBGC_SWITCH && MRBGC_FREE_LIST_TYPE==0
    f01top = f02top = f03top = f04top = f05top = NULL;
    f06top = f07top = f08top = f16top = f32top = NULL;
#if MRBGC_STATISTICS
    f01peek  = f02peek	= f03peek  = f04peek  = f05peek	 = 0;
    f06peek  = f07peek	= f08peek  = f16peek  = f32peek	 = 0;
    f01total = f02total = f03total = f04total = f05total = 0;
    f06total = f07total = f08total = f16total = f32total = 0;
    f01used  = f02used	= f03used  = f04used  = f05used	 = 0;
    f06used  = f07used	= f08used  = f16used  = f32used	 = 0;
    f99peek  = f99total = f99used  = 0;
#if MRBGC_STATISTICS == 2
    mst_deref = 0;
    mst_cslst = mst_cflst = 0;
    mst_csv01 = mst_csv02 = mst_csv03 = mst_csv04 = mst_csv05 = 0;
    mst_csv06 = mst_csv07 = mst_csv08 = mst_csv16 = mst_csv32 = 0;
    mst_cfv01 = mst_cfv02 = mst_cfv03 = mst_cfv04 = mst_cfv05 = 0;
    mst_cfv06 = mst_cfv07 = mst_cfv08 = mst_cfv16 = mst_cfv32 = 0;
    mst_cvl01 = mst_cvl02 = mst_cvl03 = mst_cvl04 = mst_cvl05 = 0;
    mst_cvl06 = mst_cvl07 = mst_cvl08 = mst_cvl16 = mst_cvl32 = 0;
    mst_cbl01 = mst_cbl02 = mst_cbl03 = mst_cbl04 = mst_cbl05 = 0;
    mst_cbl06 = mst_cbl07 = mst_cbl08 = mst_cbl16 = mst_cbl32 = 0;
    mst_rslst = mst_rflst = 0;
    mst_rsv01 = mst_rsv02 = mst_rsv03 = mst_rsv04 = mst_rsv05 = 0;
    mst_rsv06 = mst_rsv07 = mst_rsv08 = mst_rsv16 = mst_rsv32 = 0;
    mst_rfv01 = mst_rfv02 = mst_rfv03 = mst_rfv04 = mst_rfv05 = 0;
    mst_rfv06 = mst_rfv07 = mst_rfv08 = mst_rfv16 = mst_rfv32 = 0;
    mst_rbl01 = mst_rbl02 = mst_rbl03 = mst_rbl04 = mst_rbl05 = 0;
    mst_rbl06 = mst_rbl07 = mst_rbl08 = mst_rbl16 = mst_rbl32 = 0;
    mst_rsv99 = mst_rfv99 = mst_rbl99 = 0;
    mst_merge = 0;
#endif
#endif
#endif
#if MRBGC_SWITCH && MRBGC_FREE_LIST_TYPE==1
    f01top = f02top = f04top = f08top = NULL;
    f16top = f32top = f64top = f28top = NULL;
#if MRBGC_STATISTICS
    f01peek  = f02peek	= f04peek  = f08peek  = 0;
    f16peek  = f32peek	= f64peek  = f28peek  = 0;
    f01total = f02total = f04total = f08total = 0;
    f16total = f32total = f64total = f28total = 0;
    f01used  = f02used	= f04used  = f08used  = 0;
    f16used  = f32used	= f64used  = f28used  = 0;
    f99peek  = f99total = f99used  = 0;
#if MRBGC_STATISTICS == 2
    mst_deref = 0;
    mst_cslst = mst_cflst = 0;
    mst_csv01 = mst_csv02 = mst_csv04 = mst_csv08 = 0;
    mst_csv16 = mst_csv32 = mst_csv64 = mst_csv28 = 0;
    mst_cfv01 = mst_cfv02 = mst_cfv04 = mst_cfv08 = 0;
    mst_cfv16 = mst_cfv32 = mst_cfv64 = mst_cfv28 = 0;
    mst_cvl01 = mst_cvl02 = mst_cvl04 = mst_cvl08 = 0;
    mst_cvl16 = mst_cvl32 = mst_cvl64 = mst_cvl28 = 0;
    mst_cbl01 = mst_cbl02 = mst_cbl04 = mst_cbl08 = 0;
    mst_cbl16 = mst_cbl32 = mst_cbl64 = mst_cbl28 = 0;
    mst_rslst = mst_rflst = 0;
    mst_rsv01 = mst_rsv02 = mst_rsv04 = mst_rsv08 = 0;
    mst_rsv16 = mst_rsv32 = mst_rsv64 = mst_rsv28 = 0;
    mst_rfv01 = mst_rfv02 = mst_rfv04 = mst_rfv08 = 0;
    mst_rfv16 = mst_rfv32 = mst_rfv64 = mst_rfv28 = 0;
    mst_rbl01 = mst_rbl02 = mst_rbl04 = mst_rbl08 = 0;
    mst_rbl16 = mst_rbl32 = mst_rbl64 = mst_rbl28 = 0;
    mst_rsv99 = mst_rfv99 = mst_rbl99 = 0;
    mst_merge = 0;
#endif
#endif
#endif
    srec_pool_top   = NULL; srec_peek	= 0;
    grec08_pool_top = NULL; grec08_peek = 0;
    grec16_pool_top = NULL; grec16_peek = 0;
    grec32_pool_top = NULL; grec32_peek = 0;
    prec_pool_top   = NULL; prec_peek	= 0;
#if MRBGC_STATISTICS
    srec_total	 = 0; srec_used	  = 0;
    grec08_total = 0; grec08_used = 0;
    grec16_total = 0; grec16_used = 0;
    grec32_total = 0; grec32_used = 0;
    prec_total	 = 0; prec_used	  = 0;
#endif
    goal_rec_list_old = goal_rec_list;
    goal_rec_list = NULL;
    merger_rec_list_old = merger_rec_list;
    merger_rec_list = NULL;
    t3_free();
    t4_free();
    return 0;
}

#if MRBGC_SWITCH

CELL *alloc_cells_to_free_list(register unsigned int size, register unsigned int num)
{
    register CELL *p;
    /* PORT: HeapRest() is a pointer difference, int on the 32-bit
       original, so this comparison and division were unsigned there.
       Past the GC warning line it is negative; signed 64-bit
       arithmetic made num huge and overran the heap. */
    if(size*num > (unsigned int)HeapRest()) num = (unsigned int)HeapRest()/size;
    if(num == 0) num = 1;
    p = H;
    SetObjectof(p, NULL);
    while(--num){
	p += size;
	SetObjectof(p, p-size);
    }
    H = p+size;
    CheckHeap();
    return(p);
}

#if MRBGC_STATISTICS == 2

int mrbgc_statistics_collect_vector(int n)
{
#if MRBGC_FREE_LIST_TYPE == 0
    switch(n){
      case 1: mst_csv01++; break;
      case 2: mst_csv02++; break;
      case 3: mst_csv03++; break;
      case 4: mst_csv04++; break;
      case 5: mst_csv05++; break;
      case 6: mst_csv06++; break;
      case 7: mst_csv07++; break;
      case 8: mst_csv08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_csv16++; break;
      DEFAULT: if(n <= 32) mst_csv32++; break;
    }
#else
    switch(n){
      case 1: mst_csv01++; break;
      case 2: mst_csv02++; break;
      case 3: case 4: mst_csv04++; break;
      case 5: case 6: case 7: case 8: mst_csv08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_csv16++; break;
      DEFAULT:
	if(n <= 64){
	    if(n <= 32){
		mst_csv32++; break;
	    }else{
		mst_csv64++; break;
	    }
	}else{
	    if(n <= 128){
		mst_csv28++; break;
	    }
	}
    }
#endif
}

int mrbgc_statistics_collect_vector_fail(int n)
{
#if MRBGC_FREE_LIST_TYPE == 0
    switch(n){
      case 1: mst_cfv01++; break;
      case 2: mst_cfv02++; break;
      case 3: mst_cfv03++; break;
      case 4: mst_cfv04++; break;
      case 5: mst_cfv05++; break;
      case 6: mst_cfv06++; break;
      case 7: mst_cfv07++; break;
      case 8: mst_cfv08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_cfv16++; break;
      DEFAULT: if(n <= 32) mst_cfv32++; break;
    }
#else
    switch(n){
      case 1: mst_cfv01++; break;
      case 2: mst_cfv02++; break;
      case 3: case 4: mst_cfv04++; break;
      case 5: case 6: case 7: case 8: mst_cfv08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_cfv16++; break;
      DEFAULT:
	if(n <= 64){
	    if(n <= 32){
		mst_cfv32++; break;
	    }else{
		mst_cfv64++; break;
	    }
	}else{
	    if(n <= 128){
		mst_cfv28++; break;
	    }
	}
    }
#endif
}

int mrbgc_statistics_collect_value(int n)
{
#if MRBGC_FREE_LIST_TYPE == 0
    switch(n){
      case 1: mst_cvl01++; break;
      case 2: mst_cvl02++; break;
      case 3: mst_cvl03++; break;
      case 4: mst_cvl04++; break;
      case 5: mst_cvl05++; break;
      case 6: mst_cvl06++; break;
      case 7: mst_cvl07++; break;
      case 8: mst_cvl08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_cvl16++; break;
      DEFAULT: if(n <= 32) mst_cvl32++; break;
    }
#else
    switch(n){
      case 1: mst_cvl01++; break;
      case 2: mst_cvl02++; break;
      case 3: case 4: mst_cvl04++; break;
      case 5: case 6: case 7: case 8: mst_cvl08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_cvl16++; break;
      DEFAULT:
	if(n <= 64){
	    if(n <= 32){
		mst_cvl32++; break;
	    }else{
		mst_cvl64++; break;
	    }
	}else{
	    if(n <= 128){
		mst_cvl28++; break;
	    }
	}
    }
#endif
}

int mrbgc_statistics_collect_in_builtin(int n)
{
#if MRBGC_FREE_LIST_TYPE == 0
    switch(n){
      case 1: mst_cbl01++; break;
      case 2: mst_cbl02++; break;
      case 3: mst_cbl03++; break;
      case 4: mst_cbl04++; break;
      case 5: mst_cbl05++; break;
      case 6: mst_cbl06++; break;
      case 7: mst_cbl07++; break;
      case 8: mst_cbl08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_cbl16++; break;
      DEFAULT: if(n <= 32) mst_cbl32++; break;
    }
#else
    switch(n){
      case 1: mst_cbl01++; break;
      case 2: mst_cbl02++; break;
      case 3: case 4: mst_cbl04++; break;
      case 5: case 6: case 7: case 8: mst_cbl08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_cbl16++; break;
      DEFAULT:
	if(n <= 64){
	    if(n <= 32){
		mst_cbl32++; break;
	    }else{
		mst_cbl64++; break;
	    }
	}else{
	    if(n <= 128){
		mst_cbl28++; break;
	    }
	}
    }
#endif
}

int mrbgc_statistics_reuse_vector(int n)
{
#if MRBGC_FREE_LIST_TYPE == 0
    switch(n){
      case 1: mst_rsv01++; f01total++; break;
      case 2: mst_rsv02++; f02total++; break;
      case 3: mst_rsv03++; f03total++; break;
      case 4: mst_rsv04++; f04total++; break;
      case 5: mst_rsv05++; f05total++; break;
      case 6: mst_rsv06++; f06total++; break;
      case 7: mst_rsv07++; f07total++; break;
      case 8: mst_rsv08++; f08total++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_rsv16++; f16total++; break;
      DEFAULT:
	if(n <= 32){
	    mst_rsv32++; f32total++; break;
	}else{
	    mst_rsv99 += n; f99total += n; break;
	}
    }
#else
    switch(n){
      case 1: mst_rsv01++; f01total++; break;
      case 2: mst_rsv02++; f02total++; break;
      case 3: case 4: mst_rsv04++; f04total++; break;
      case 5: case 6: case 7: case 8: mst_rsv08++; f08total++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_rsv16++; f16total++; break;
      DEFAULT:
	if(n <= 64){
	    if(n <= 32){
		mst_rsv32++; f32total++; break;
	    }else{
		mst_rsv64++; f64total++; break;
	    }
	}else{
	    if(n <= 128){
		mst_rsv28++; f28total++; break;
	    }else{
		mst_rsv99 += n; f99total += n; break;
	    }
	}
    }
#endif
}

int mrbgc_statistics_reuse_vector_fail(int n)
{
#if MRBGC_FREE_LIST_TYPE == 0
    switch(n){
      case 1: mst_rfv01++; break;
      case 2: mst_rfv02++; break;
      case 3: mst_rfv03++; break;
      case 4: mst_rfv04++; break;
      case 5: mst_rfv05++; break;
      case 6: mst_rfv06++; break;
      case 7: mst_rfv07++; break;
      case 8: mst_rfv08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_rfv16++; break;
      DEFAULT: if(n <= 32) mst_rfv32++; else mst_rfv99 += n; break;
    }
#else
    switch(n){
      case 1: mst_rfv01++; break;
      case 2: mst_rfv02++; break;
      case 3: case 4: mst_rfv04++; break;
      case 5: case 6: case 7: case 8: mst_rfv08++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_rfv16++; break;
      DEFAULT:
	if(n <= 64){
	    if(n <= 32){
		mst_rfv32++; break;
	    }else{
		mst_rfv64++; break;
	    }
	}else{
	    if(n <= 128){
		mst_rfv28++; break;
	    }else{
		mst_rfv99 += n; break;
	    }
	}
    }
#endif
}

int mrbgc_statistics_reuse_in_builtin(int n)
{
#if MRBGC_FREE_LIST_TYPE == 0
    switch(n){
      case 1: mst_rbl01++; f01total++; break;
      case 2: mst_rbl02++; f02total++; break;
      case 3: mst_rbl03++; f03total++; break;
      case 4: mst_rbl04++; f04total++; break;
      case 5: mst_rbl05++; f05total++; break;
      case 6: mst_rbl06++; f06total++; break;
      case 7: mst_rbl07++; f07total++; break;
      case 8: mst_rbl08++; f08total++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_rbl16++; f16total++; break;
      DEFAULT:
	if(n <= 32){
	    mst_rbl32++; f32total++; break;
	}else{
	    mst_rbl99 += n; f99total += n; break;
	}
    }
#else
    switch(n){
      case 1: mst_rbl01++; f01total++; break;
      case 2: mst_rbl02++; f02total++; break;
      case 3: case 4: mst_rbl04++; f04total++; break;
      case 5: case 6: case 7: case 8: mst_rbl08++; f08total++; break;
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:
	mst_rbl16++; f16total++; break;
      DEFAULT:
	if(n <= 64){
	    if(n <= 32){
		mst_rbl32++; f32total++; break;
	    }else{
		mst_rbl64++; f64total++; break;
	    }
	}else{
	    if(n <= 128){
		mst_rbl28++; f28total++; break;
	    }else{
		mst_rbl99 += n; f99total += n; break;
	    }
	}
    }
#endif
}

#endif
#endif

/*************************************************************************
*   Heap Area Management -- Record.					 *
*************************************************************************/

int alloc_suspension_record(register unsigned int num)
{
    register SUSPENSION_RECORD *p;
    if((uint32_t)(num*sizeof(SUSPENSION_RECORD)) > (uint32_t)(HeapRest()*sizeof(CELL)))	/* MODERN: 32-bit arithmetic, as on the original */
	num = (uint32_t)(HeapRest()*sizeof(CELL))/sizeof(SUSPENSION_RECORD);
    if(num == 0) num = 1;
    p = (SUSPENSION_RECORD *)H;
    p->other = 0;
    while(--num){
	p++;
	p->other = Ref(p-1);
    }
    H = (CELL *)(p+1);
    srec_pool_top = p;
    CheckHeap();
    return 0;
}

int alloc_goal_record8(register unsigned int num)
{
    register GOAL_RECORD *p1, *p2;
    if((uint32_t)(num*sizeof(GOAL_RECORD)) > (uint32_t)(HeapRest()*sizeof(CELL)))	/* MODERN: 32-bit arithmetic, as on the original */
	num = (uint32_t)(HeapRest()*sizeof(CELL))/sizeof(GOAL_RECORD);
    if(num == 0) num = 1;
    p1 = (GOAL_RECORD *)H;
    SetGoalQueuePt2(p1, NULL);
    p1->next = Ref(goal_rec_list);
    p1->parent = 0;
    p2 = p1++;
    while(--num){
	SetGoalQueuePt2(p1, p2);
	p1->next = Ref(p2);
	p1->parent = 0;
	p2 = p1++;
    }
    H = (CELL *)p1;
    grec08_pool_top = p2;
    goal_rec_list = p2;
    CheckHeap();
    return 0;
}

int alloc_goal_record16(register unsigned int num)
{
    register GOAL_RECORD16 *p1, *p2;
    if((uint32_t)(num*sizeof(GOAL_RECORD16)) > (uint32_t)(HeapRest()*sizeof(CELL)))	/* MODERN: 32-bit arithmetic, as on the original */
	num = (uint32_t)(HeapRest()*sizeof(CELL))/sizeof(GOAL_RECORD16);
    if(num == 0) num = 1;
    p1 = (GOAL_RECORD16 *)H;
    SetGoalQueuePt2(p1, NULL);
    p1->next = Ref((GOAL_RECORD16 *)goal_rec_list);
    p1->parent = 0;
    p2 = p1++;
    while(--num){
	SetGoalQueuePt2(p1, p2);
	p1->next = Ref(p2);
	p1->parent = 0;
	p2 = p1++;
    }
    H = (CELL *)p1;
    grec16_pool_top = p2;
    goal_rec_list = (GOAL_RECORD *)p2;
    CheckHeap();
    return 0;
}

int alloc_goal_record32(register unsigned int num)
{
    register GOAL_RECORD32 *p1, *p2;
    if((uint32_t)(num*sizeof(GOAL_RECORD32)) > (uint32_t)(HeapRest()*sizeof(CELL)))	/* MODERN: 32-bit arithmetic, as on the original */
	num = (uint32_t)(HeapRest()*sizeof(CELL))/sizeof(GOAL_RECORD32);
    if(num == 0) num = 1;
    p1 = (GOAL_RECORD32 *)H;
    SetGoalQueuePt2(p1, NULL);
    p1->next = Ref((GOAL_RECORD32 *)goal_rec_list);
    p1->parent = 0;
    p2 = p1++;
    while(--num){
	SetGoalQueuePt2(p1, p2);
	p1->next = Ref(p2);
	p1->parent = 0;
	p2 = p1++;
    }
    H = (CELL *)p1;
    grec32_pool_top = p2;
    goal_rec_list = (GOAL_RECORD *)p2;
    CheckHeap();
    return 0;
}

int alloc_parent_record(register unsigned int num)
{
    register PARENT_RECORD *p;
    if((uint32_t)(num*sizeof(PARENT_RECORD)) > (uint32_t)(HeapRest()*sizeof(CELL)))	/* MODERN: 32-bit arithmetic, as on the original */
	num = (uint32_t)(HeapRest()*sizeof(CELL))/sizeof(PARENT_RECORD);
    if(num == 0) num = 1;
    p = (PARENT_RECORD *)H;
    p->parent = 0;
    while(--num){
	p++;
	p->parent = Ref(p-1);
    }
    H = (CELL *)(p+1);
    prec_pool_top = p;
    CheckHeap();
    return 0;
}

unsigned int count_suspension_record_in_free_list(void)
{
    register SUSPENSION_RECORD *p;
    register unsigned int n = 0;
    for(p = srec_pool_top; p != NULL; p = SrecOf(p->other)) n++;
    return(n);
}

unsigned int count_goal_record8_in_free_list(void)
{
    register GOAL_RECORD *p;
    register unsigned int n = 0;
    for(p = grec08_pool_top; p != NULL; p = GoalQueuePt(p)) n++;
    return(n);
}

unsigned int count_goal_record16_in_free_list(void)
{
    register GOAL_RECORD16 *p;
    register unsigned int n = 0;
    for(p=grec16_pool_top; p!=NULL; p=(GOAL_RECORD16 *)GoalQueuePt(p)) n++;
    return(n);
}

unsigned int count_goal_record32_in_free_list(void)
{
    register GOAL_RECORD32 *p;
    register unsigned int n = 0;
    for(p=grec32_pool_top; p!=NULL; p=(GOAL_RECORD32 *)GoalQueuePt(p)) n++;
    return(n);
}

unsigned int count_parent_record_in_free_list(void)
{
    register PARENT_RECORD *p;
    register unsigned int n = 0;
    for(p = prec_pool_top; p != NULL; p = PrecOf(p->parent)) n++;
    return(n);
}


/*************************************************************************
*   Code Area Management.						 *
*************************************************************************/

#define CODEWARN 64

int code_size, code_size_all;
OBJ *C, *code_base, *user_code, *user_code_limit;
OBJ *code1, *code1_warn, *code1_limit;	/* Current Set */
OBJ *code2, *code2_warn, *code2_limit;	/* Another Set */

int initialize_code(unsigned int size)
{
    size = (size+7)&0xFFFFFFF8;
    code_size_all = size;
    code_size = (size/5)*4;
    code_base = (OBJ *)malloc(sizeof(OBJ) * size);
    if(code_base == NULL){
	Error("Not Enough Memory (malloc failure, code) -- Aborted.");
	exit_pdss(1);
    }
    user_code = code_base;
    code1 = user_code;
    code1_limit = code1+code_size;
    code1_warn = code1_limit-CODEWARN;
    code2 = user_code+code_size;
    code2_limit = code_base+size;
    code2_warn = code2_limit-CODEWARN;
    user_code_limit = code2_limit;
    C = code1;
    t1_free();
    t2_free();
    return 0;
}

int initialize_code2(void)
{
    unsigned int size;
    C += (8 - ((uintptr_t)C & 7)) & 7;
    size = code_base+code_size_all-C;
    code_size = size/2;
    user_code = C;
    code1 = user_code;
    code1_limit = code1+code_size;
    code1_warn = code1_limit-CODEWARN;
    code2 = user_code+code_size;
    code2_limit = code2+code_size;
    code2_warn = code2_limit-CODEWARN;
    user_code_limit = code2_limit;
    t1_free();
    t2_free();
    return 0;
}

int switch_code(void)
{
    OBJ *work;

    work = code1;	code1	    = code2;	   code2       = work;
    work = code1_limit; code1_limit = code2_limit; code2_limit = work;
    work = code1_warn;	code1_warn  = code2_warn;  code2_warn  = work;
    C = code1;
    t1_free();
    t2_free();
    return 0;
}


/*************************************************************************
*   Temporary Area Management.						 *
*************************************************************************/

/* MODERN: the 1992 code rounded sizes to 4 bytes, enough when a pointer
   was 4 bytes; the assembler keeps structs with host pointers here, so a
   block is aligned for them (TEMP_ALIGN, at least 4). */
struct temp_align_probe { char c; union { void *p; double d; long l; int32_t i; } u; };
#define TEMP_ALIGN	offsetof(struct temp_align_probe, u)
#define TempAlignDown(p) ((unsigned char *)(p) - ((uintptr_t)(p) % TEMP_ALIGN))
#define TempAlignUp(p)	 ((unsigned char *)(p) + ((TEMP_ALIGN - (uintptr_t)(p) % TEMP_ALIGN) % TEMP_ALIGN))

static unsigned char *temp1_top;
static unsigned char *temp2_top;
static unsigned char *temp3_top;
static unsigned char *temp4_top;

unsigned char *t1_alloc(unsigned int size)
{
    temp1_top = TempAlignDown(temp1_top - size);
    return(temp1_top);
}

int t1_free(void)
{
    temp1_top = (unsigned char *)code2_limit;
    return 0;
}

unsigned char *t2_alloc(unsigned int size)
{
    unsigned char *p;
    p = TempAlignUp(temp2_top);
    temp2_top = p + size;
    return(p);
}

int t2_free(void)
{
    temp2_top = (unsigned char *)code2;
    return 0;
}

unsigned char *t3_alloc(unsigned int size)
{
    temp3_top = TempAlignDown(temp3_top - size);
    return(temp3_top);
}

int t3_free(void)
{
    temp3_top = (unsigned char *)heap2_limit;
    return 0;
}

unsigned char *t4_alloc(unsigned int size)
{
    unsigned char *p;
    p = TempAlignUp(temp4_top);
    temp4_top = p + size;
    return(p);
}

int t4_free(void)
{
    temp4_top = (unsigned char *)heap2;
    return 0;
}
