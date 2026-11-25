/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

extern int  heap_size;
extern CELL *H;
extern CELL *heap1, *heap1_warn, *heap1_limit;	/* Current Set */
extern CELL *heap2, *heap2_warn, *heap2_limit;	/* Another Set */

extern int  code_size, code_size_all;
extern OBJ  *C, *code_base, *user_code, *user_code_limit;
extern OBJ  *code1, *code1_warn, *code1_limit;	/* Current Set */
extern OBJ  *code2, *code2_warn, *code2_limit;	/* Another Set */

extern CHAR *mesg_heap_area_overflow;
extern CHAR *mesg_code_area_overflow;

#if MRBGC_SWITCH
#endif


/*************************************************************************
*   Heap Area Management -- Common.					 *
*************************************************************************/

#define HeapSize() heap_size
#define HeapUsed() (H-heap1)
#define HeapRest() (heap1_warn-H)
#define HeapUsedKL1()\
    (((size_t)((char *)H - (char *)heap1)\
	-(srec_peek   * sizeof(SUSPENSION_RECORD))\
	-(grec08_peek * sizeof(GOAL_RECORD))\
	-(grec16_peek * sizeof(GOAL_RECORD16))\
	-(grec32_peek * sizeof(GOAL_RECORD32))\
	-(prec_peek   * sizeof(PARENT_RECORD)))\
	/ sizeof(CELL))

#define CheckHeap()\
    if(H >= heap1_warn){\
	if(H >= heap1_limit){\
	    Error(mesg_heap_area_overflow);\
	    exit_pdss(1);\
	}else{\
	    SetHeapGcFlag();\
	}\
    }

#define InHeap(p)\
    ((((CELL *)(p)) >= heap1 && ((CELL *)(p)) < heap1_limit) ||\
     (((CELL *)(p)) >= heap2 && ((CELL *)(p)) < heap2_limit))
#define InActiveHeap(p)\
    (((CELL *)(p)) >= heap1 && ((CELL *)(p)) < heap1_limit)
#define InOldHeap(p)\
    (((CELL *)(p)) >= heap2 && ((CELL *)(p)) < heap2_limit)


/*************************************************************************
*   Heap Area Management -- Without MRB-GC.				 *
*************************************************************************/
#if !MRBGC_SWITCH

#define Alloc1Word(c)	  { (c) = H++; CheckHeap(); }
#define Alloc2Words(c)	  { (c) = H; H += 2; CheckHeap(); }
#define AllocNWords(c,n)  { (c) = H; H += (n); CheckHeap(); }
#define AllocNWords2(c,n) { (c) = H; H += (n); CheckHeap(); }

#define GcAlloc1Word(c)	    { (c) = H++; }
#define GcAlloc2Words(c)    { (c) = H; H += 2; }
#define GcAllocNWords(c,n)  { (c) = H; H += (n); }
#define GcAllocNWords2(c,n) { (c) = H; H += (n); }

#define Free1Word(c)
#define Free2Words(c)
#define FreeNWords(c,n)
#define FreeNWords2(c,n)

#endif
/*************************************************************************
*   Heap Area Management -- With MRB-GC.				 *
*************************************************************************/
#if MRBGC_SWITCH

#if MRBGC_STATISTICS
#define AllocCells(C, N, Top, Peek, Total, Used, Alloc){\
    if(Top){\
	(C) = Top; Top = Objectof(Top);\
    }else{\
	(C) = H; H += (N);\
	CheckHeap();\
	Peek++;\
    }\
    Total++; Used++;\
}
#else
#define AllocCells(C, N, Top, Peek, Total, Used, Alloc){\
    if(Top == NULL) Top = alloc_cells_to_free_list(N, Alloc);\
    (C) = Top; Top = Objectof(Top);\
}
#endif

#if MRBGC_STATISTICS
#define GcAllocCells(C, N, Peek, Total, Used){\
    (C) = H; H += (N);\
    Peek++; Total++; Used++;\
}
#else
#define GcAllocCells(C, N, Peek, Total, Used){\
    (C) = H; H += (N);\
}
#endif

#if MRBGC_STATISTICS
#define AllocBig(C, N){\
    (C) = H; H += (N); CheckHeap();\
    f99peek += (N); f99total += (N); f99used += (N);\
}
#else
#define AllocBig(C, N){\
    (C) = H; H += (N); CheckHeap();\
}
#endif

#if MRBGC_STATISTICS
#define GcAllocBig(C, N){\
    (C) = H; H += (N);\
    f99peek += (N); f99total += (N); f99used += (N);\
}
#else
#define GcAllocBig(C, N){\
    (C) = H; H += (N);\
}
#endif

#if MRBGC_STATISTICS
#define FreeCells(C, Top, Used){\
    register CELL *p = Top;\
    Top = (C); SetObjectof(Top, p);\
    Used--;\
}
#else
#define FreeCells(C, Top, Used){\
    register CELL *p = Top;\
    Top = (C); SetObjectof(Top, p);\
}
#endif

#endif
/*************************************************************************
*   MRB-GC #1 -- Free List: 1W, 2W, 3W, 4W, 5W, 6W, 7W, 8W, 16W, 32W.	 *
*************************************************************************/
#if MRBGC_SWITCH && MRBGC_FREE_LIST_TYPE==0

extern CELL *f01top,  *f02top,	*f03top,  *f04top,  *f05top;
extern CELL *f06top,  *f07top,	*f08top,  *f16top,  *f32top;
#if MRBGC_STATISTICS
extern int  f01peek,  f02peek,	f03peek,  f04peek,  f05peek;
extern int  f06peek,  f07peek,	f08peek,  f16peek,  f32peek,  f99peek;
extern int  f01total, f02total, f03total, f04total, f05total;
extern int  f06total, f07total, f08total, f16total, f32total, f99total;
extern int  f01used,  f02used,	f03used,  f04used,  f05used;
extern int  f06used,  f07used,	f08used,  f16used,  f32used,  f99used;
#if MRBGC_STATISTICS == 2
extern int  mst_deref;
extern int  mst_cslst, mst_cflst;
extern int  mst_csv01, mst_csv02, mst_csv03, mst_csv04, mst_csv05;
extern int  mst_csv06, mst_csv07, mst_csv08, mst_csv16, mst_csv32;
extern int  mst_cfv01, mst_cfv02, mst_cfv03, mst_cfv04, mst_cfv05;
extern int  mst_cfv06, mst_cfv07, mst_cfv08, mst_cfv16, mst_cfv32;
extern int  mst_cvl01, mst_cvl02, mst_cvl03, mst_cvl04, mst_cvl05;
extern int  mst_cvl06, mst_cvl07, mst_cvl08, mst_cvl16, mst_cvl32;
extern int  mst_cbl01, mst_cbl02, mst_cbl03, mst_cbl04, mst_cbl05;
extern int  mst_cbl06, mst_cbl07, mst_cbl08, mst_cbl16, mst_cbl32;
extern int  mst_rslst, mst_rflst;
extern int  mst_rsv01, mst_rsv02, mst_rsv03, mst_rsv04, mst_rsv05;
extern int  mst_rsv06, mst_rsv07, mst_rsv08, mst_rsv16, mst_rsv32, mst_rsv99;
extern int  mst_rfv01, mst_rfv02, mst_rfv03, mst_rfv04, mst_rfv05;
extern int  mst_rfv06, mst_rfv07, mst_rfv08, mst_rfv16, mst_rfv32, mst_rfv99;
extern int  mst_rbl01, mst_rbl02, mst_rbl03, mst_rbl04, mst_rbl05;
extern int  mst_rbl06, mst_rbl07, mst_rbl08, mst_rbl16, mst_rbl32, mst_rbl99;
extern int  mst_merge;
#endif
#endif

#define Alloc1Word(C)	AllocCells(C, 1,f01top,f01peek,f01total,f01used,100)
#define Alloc2Words(C)	AllocCells(C, 2,f02top,f02peek,f02total,f02used, 50)
#define Alloc3Words(C)	AllocCells(C, 3,f03top,f03peek,f03total,f03used, 20)
#define Alloc4Words(C)	AllocCells(C, 4,f04top,f04peek,f04total,f04used, 10)
#define Alloc5Words(C)	AllocCells(C, 5,f05top,f05peek,f05total,f05used, 10)
#define Alloc6Words(C)	AllocCells(C, 6,f06top,f06peek,f06total,f06used, 10)
#define Alloc7Words(C)	AllocCells(C, 7,f07top,f07peek,f07total,f07used, 10)
#define Alloc8Words(C)	AllocCells(C, 8,f08top,f08peek,f08total,f08used, 10)
#define Alloc16Words(C) AllocCells(C,16,f16top,f16peek,f16total,f16used, 10)
#define Alloc32Words(C) AllocCells(C,32,f32top,f32peek,f32total,f32used, 10)
#define AllocNWords(C,N){\
    switch(N){\
      case 1: Alloc1Word(C);  break;\
      case 2: Alloc2Words(C); break;\
      case 3: Alloc3Words(C); break;\
      case 4: Alloc4Words(C); break;\
      case 5: Alloc5Words(C); break;\
      case 6: Alloc6Words(C); break;\
      case 7: Alloc7Words(C); break;\
      case 8: Alloc8Words(C); break;\
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:\
	Alloc16Words(C); break;\
      DEFAULT:\
	if((N) <= 32){\
	    Alloc32Words(C);\
	}else{\
	    AllocBig(C,N);\
	}\
    }\
}
#define AllocNWords2(C,N){\
    if	   ((N) ==  1){ Alloc1Word(C);	 }\
    else if((N) ==  2){ Alloc2Words(C);	 }\
    else if((N) ==  3){ Alloc3Words(C);	 }\
    else if((N) ==  4){ Alloc4Words(C);	 }\
    else if((N) ==  5){ Alloc5Words(C);	 }\
    else if((N) ==  6){ Alloc6Words(C);	 }\
    else if((N) ==  7){ Alloc7Words(C);	 }\
    else if((N) ==  8){ Alloc8Words(C);	 }\
    else if((N) <= 16){ Alloc16Words(C); }\
    else if((N) <= 32){ Alloc32Words(C); }\
    else {		AllocBig(C,N);	 }\
}

#define GcAlloc1Word(C)	  GcAllocCells(C, 1,f01peek,f01total,f01used)
#define GcAlloc2Words(C)  GcAllocCells(C, 2,f02peek,f02total,f02used)
#define GcAlloc3Words(C)  GcAllocCells(C, 3,f03peek,f03total,f03used)
#define GcAlloc4Words(C)  GcAllocCells(C, 4,f04peek,f04total,f04used)
#define GcAlloc5Words(C)  GcAllocCells(C, 5,f05peek,f05total,f05used)
#define GcAlloc6Words(C)  GcAllocCells(C, 6,f06peek,f06total,f06used)
#define GcAlloc7Words(C)  GcAllocCells(C, 7,f07peek,f07total,f07used)
#define GcAlloc8Words(C)  GcAllocCells(C, 8,f08peek,f08total,f08used)
#define GcAlloc16Words(C) GcAllocCells(C,16,f16peek,f16total,f16used)
#define GcAlloc32Words(C) GcAllocCells(C,32,f32peek,f32total,f32used)
#define GcAllocNWords(C,N){\
    switch(N){\
      case 1: GcAlloc1Word(C);	break;\
      case 2: GcAlloc2Words(C); break;\
      case 3: GcAlloc3Words(C); break;\
      case 4: GcAlloc4Words(C); break;\
      case 5: GcAlloc5Words(C); break;\
      case 6: GcAlloc6Words(C); break;\
      case 7: GcAlloc7Words(C); break;\
      case 8: GcAlloc8Words(C); break;\
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:\
	GcAlloc16Words(C); break;\
      DEFAULT:\
	if((N) <= 32){\
	    GcAlloc32Words(C);\
	}else{\
	    GcAllocBig(C,N);\
	}\
    }\
}
#define GcAllocNWords2(C,N){\
    if	   ((N) ==  1){ GcAlloc1Word(C);   }\
    else if((N) ==  2){ GcAlloc2Words(C);  }\
    else if((N) ==  3){ GcAlloc3Words(C);  }\
    else if((N) ==  4){ GcAlloc4Words(C);  }\
    else if((N) ==  5){ GcAlloc5Words(C);  }\
    else if((N) ==  6){ GcAlloc6Words(C);  }\
    else if((N) ==  7){ GcAlloc7Words(C);  }\
    else if((N) ==  8){ GcAlloc8Words(C);  }\
    else if((N) <= 16){ GcAlloc16Words(C); }\
    else if((N) <= 32){ GcAlloc32Words(C); }\
    else {		GcAllocBig(C,N);   }\
}

#define Free1Word(C)   FreeCells(C,f01top,f01used)
#define Free2Words(C)  FreeCells(C,f02top,f02used)
#define Free3Words(C)  FreeCells(C,f03top,f03used)
#define Free4Words(C)  FreeCells(C,f04top,f04used)
#define Free5Words(C)  FreeCells(C,f05top,f05used)
#define Free6Words(C)  FreeCells(C,f06top,f06used)
#define Free7Words(C)  FreeCells(C,f07top,f07used)
#define Free8Words(C)  FreeCells(C,f08top,f08used)
#define Free16Words(C) FreeCells(C,f16top,f16used)
#define Free32Words(C) FreeCells(C,f32top,f32used)
#define FreeNWords(C,N){\
    switch(N){\
      case 1: Free1Word(C);  break;\
      case 2: Free2Words(C); break;\
      case 3: Free3Words(C); break;\
      case 4: Free4Words(C); break;\
      case 5: Free5Words(C); break;\
      case 6: Free6Words(C); break;\
      case 7: Free7Words(C); break;\
      case 8: Free8Words(C); break;\
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:\
	Free16Words(C); break;\
      DEFAULT: if((N) <= 32) Free32Words(C);\
    }\
}
#define FreeNWords2(C,N){\
    if	   ((N) ==  1){ Free1Word(C);	}\
    else if((N) ==  2){ Free2Words(C);	}\
    else if((N) ==  3){ Free3Words(C);	}\
    else if((N) ==  4){ Free4Words(C);	}\
    else if((N) ==  5){ Free5Words(C);	}\
    else if((N) ==  6){ Free6Words(C);	}\
    else if((N) ==  7){ Free7Words(C);	}\
    else if((N) ==  8){ Free8Words(C);	}\
    else if((N) <= 16){ Free16Words(C); }\
    else if((N) <= 32){ Free32Words(C); }\
}

#endif
/*************************************************************************
*   MRB-GC #2 -- Free List: 1W, 2W, 4W, 8W, 16W, 32W, 64W, 128W.	 *
*************************************************************************/
#if MRBGC_SWITCH && MRBGC_FREE_LIST_TYPE==1

extern CELL *f01top,  *f02top,	*f04top,  *f08top;
extern CELL *f16top,  *f32top,	*f64top,  *f28top;
#if MRBGC_STATISTICS
extern int  f01peek,  f02peek,	f04peek,  f08peek;
extern int  f16peek,  f32peek,	f64peek,  f28peek,  f99peek;
extern int  f01total, f02total, f04total, f08total;
extern int  f16total, f32total, f64total, f28total, f99total;
extern int  f01used,  f02used,	f04used,  f08used;
extern int  f16used,  f32used,	f64used,  f28used,  f99used;
#if MRBGC_STATISTICS == 2
extern int  mst_deref;
extern int  mst_cslst, mst_cflst;
extern int  mst_csv01, mst_csv02, mst_csv04, mst_csv08;
extern int  mst_csv16, mst_csv32, mst_csv64, mst_csv28;
extern int  mst_cfv01, mst_cfv02, mst_cfv04, mst_cfv08;
extern int  mst_cfv16, mst_cfv32, mst_cfv64, mst_cfv28;
extern int  mst_cvl01, mst_cvl02, mst_cvl04, mst_cvl08;
extern int  mst_cvl16, mst_cvl32, mst_cvl64, mst_cvl28;
extern int  mst_cbl01, mst_cbl02, mst_cbl04, mst_cbl08;
extern int  mst_cbl16, mst_cbl32, mst_cbl64, mst_cbl28;
extern int  mst_rslst, mst_rflst;
extern int  mst_rsv01, mst_rsv02, mst_rsv04, mst_rsv08;
extern int  mst_rsv16, mst_rsv32, mst_rsv64, mst_rsv28, mst_rsv99;
extern int  mst_rfv01, mst_rfv02, mst_rfv04, mst_rfv08;
extern int  mst_rfv16, mst_rfv32, mst_rfv64, mst_rfv28, mst_rfv99;
extern int  mst_rbl01, mst_rbl02, mst_rbl04, mst_rbl08;
extern int  mst_rbl16, mst_rbl32, mst_rbl64, mst_rbl28, mst_rbl99;
extern int  mst_merge;
#endif
#endif

#define Alloc1Word(C)	 AllocCells(C,	1,f01top,f01peek,f01total,f01used,100)
#define Alloc2Words(C)	 AllocCells(C,	2,f02top,f02peek,f02total,f02used, 50)
#define Alloc4Words(C)	 AllocCells(C,	4,f04top,f04peek,f04total,f04used, 25)
#define Alloc8Words(C)	 AllocCells(C,	8,f08top,f08peek,f08total,f08used, 12)
#define Alloc16Words(C)	 AllocCells(C, 16,f16top,f16peek,f16total,f16used,  6)
#define Alloc32Words(C)	 AllocCells(C, 32,f32top,f32peek,f32total,f32used,  3)
#define Alloc64Words(C)	 AllocCells(C, 64,f64top,f64peek,f64total,f64used,  2)
#define Alloc128Words(C) AllocCells(C,128,f28top,f28peek,f28total,f28used,  1)
#define AllocNWords(C,N){\
    switch(N){\
      case 1:\
	Alloc1Word(C); break;\
      case 2:\
	Alloc2Words(C); break;\
      case 3: case 4:\
	Alloc4Words(C); break;\
      case 5: case 6: case 7: case 8:\
	Alloc8Words(C); break;\
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:\
	Alloc16Words(C); break;\
      DEFAULT:\
	if((N) <= 64){\
	    if((N) <= 32){\
		Alloc32Words(C);\
	    }else{\
		Alloc64Words(C);\
	    }\
	}else{\
	    if((N) <= 128){\
		Alloc128Words(C);\
	    }else{\
		AllocBig(C,N);\
	    }\
	}\
    }\
}
#define AllocNWords2(C,N){\
    if	   ((N) ==   1){ Alloc1Word(C);	   }\
    else if((N) ==   2){ Alloc2Words(C);   }\
    else if((N) <=   4){ Alloc4Words(C);   }\
    else if((N) <=   8){ Alloc8Words(C);   }\
    else if((N) <=  16){ Alloc16Words(C);  }\
    else if((N) <=  32){ Alloc32Words(C);  }\
    else if((N) <=  64){ Alloc64Words(C);  }\
    else if((N) <= 128){ Alloc128Words(C); }\
    else {		 AllocBig(C,N);	   }\
}

#define GcAlloc1Word(C)	   GcAllocCells(C,  1,f01peek,f01total,f01used)
#define GcAlloc2Words(C)   GcAllocCells(C,  2,f02peek,f02total,f02used)
#define GcAlloc4Words(C)   GcAllocCells(C,  4,f04peek,f04total,f04used)
#define GcAlloc8Words(C)   GcAllocCells(C,  8,f08peek,f08total,f08used)
#define GcAlloc16Words(C)  GcAllocCells(C, 16,f16peek,f16total,f16used)
#define GcAlloc32Words(C)  GcAllocCells(C, 32,f32peek,f32total,f32used)
#define GcAlloc64Words(C)  GcAllocCells(C, 64,f64peek,f64total,f64used)
#define GcAlloc128Words(C) GcAllocCells(C,128,f28peek,f28total,f28used)
#define GcAllocNWords(C,N){\
    switch(N){\
      case 1:\
	GcAlloc1Word(C); break;\
      case 2:\
	GcAlloc2Words(C); break;\
      case 3: case 4:\
	GcAlloc4Words(C); break;\
      case 5: case 6: case 7: case 8:\
	GcAlloc8Words(C); break;\
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:\
	GcAlloc16Words(C); break;\
      DEFAULT:\
	if((N) <= 64){\
	    if((N) <= 32){\
		GcAlloc32Words(C);\
	    }else{\
		GcAlloc64Words(C);\
	    }\
	}else{\
	    if((N) <= 128){\
		GcAlloc128Words(C);\
	    }else{\
		GcAllocBig(C,N);\
	    }\
	}\
    }\
}
#define GcAllocNWords2(C,N){\
    if	   ((N) ==   1){ GcAlloc1Word(C);    }\
    else if((N) ==   2){ GcAlloc2Words(C);   }\
    else if((N) <=   4){ GcAlloc4Words(C);   }\
    else if((N) <=   8){ GcAlloc8Words(C);   }\
    else if((N) <=  16){ GcAlloc16Words(C);  }\
    else if((N) <=  32){ GcAlloc32Words(C);  }\
    else if((N) <=  64){ GcAlloc64Words(C);  }\
    else if((N) <= 128){ GcAlloc128Words(C); }\
    else {		 GcAllocBig(C,N);    }\
}

#define Free1Word(C)	FreeCells(C,f01top,f01used)
#define Free2Words(C)	FreeCells(C,f02top,f02used)
#define Free4Words(C)	FreeCells(C,f04top,f04used)
#define Free8Words(C)	FreeCells(C,f08top,f08used)
#define Free16Words(C)	FreeCells(C,f16top,f16used)
#define Free32Words(C)	FreeCells(C,f32top,f32used)
#define Free64Words(C)	FreeCells(C,f64top,f64used)
#define Free128Words(C) FreeCells(C,f28top,f28used)
#define FreeNWords(C,N){\
    switch(N){\
      case 1:\
	Free1Word(C); break;\
      case 2:\
	Free2Words(C); break;\
      case 3: case 4:\
	Free4Words(C); break;\
      case 5: case 6: case 7: case 8:\
	Free8Words(C); break;\
      case 9: case 10: case 11: case 12: case 13: case 14: case 15: case 16:\
	Free16Words(C); break;\
      DEFAULT:\
	if((N) <= 64){\
	    if((N) <= 32){\
		Free32Words(C);\
	    }else{\
		Free64Words(C);\
	    }\
	}else{\
	    if((N) <= 128){\
		Free128Words(C);\
	    }\
	}\
    }\
}
#define FreeNWords2(C,N){\
    if	   ((N) ==   1){ Free1Word(C);	  }\
    else if((N) ==   2){ Free2Words(C);	  }\
    else if((N) <=   4){ Free4Words(C);	  }\
    else if((N) <=   8){ Free8Words(C);	  }\
    else if((N) <=  16){ Free16Words(C);  }\
    else if((N) <=  32){ Free32Words(C);  }\
    else if((N) <=  64){ Free64Words(C);  }\
    else if((N) <= 128){ Free128Words(C); }\
}

#endif
/*************************************************************************
*   Alloc / Free KL1 Data.						 *
*************************************************************************/

#define AllocCell(C)	  { Alloc1Word(C); }
#define AllocVoid(C)\
	{ Alloc1Word(C); SetAll(C,UNDEF,NULL,MRBOFF); }
#define AllocUndef(C)\
	{ Alloc1Word(C); SetAll(C,UNDEF,NULL,MRBON); }
#define AllocMghok(C)\
	{ Alloc1Word(C); SetTypeof(C,MGHOK); SetMrbof(C,MRBON); }
#define AllocFloat(C)	  { Alloc2Words(C); }
#define AllocCons(C)	  { Alloc2Words(C); }
#define AllocVector(C,N)  { AllocNWords(C,(N)+1); SetAll(C,DESC,N,MRBOFF); }
#define AllocVector2(C,N) { AllocNWords2(C,(N)+1); SetAll(C,DESC,N,MRBOFF); }
#define AllocString(C,N)  { AllocNWords(C,(N)+1); }
#define AllocString2(C,N) { AllocNWords2(C,(N)+1); }

#define FreeCell(C)	  { Free1Word(C); }
#define FreeFloat(C)	  { Free2Words(C); }
#define FreeCons(C)	  { Free2Words(C); }
#define FreeVector(C,N)	  { FreeNWords(C,(N)+1); }
#define FreeVector2(C,N)  { FreeNWords2(C,(N)+1); }
#define FreeString(C,N)	  { FreeNWords(C,(N)+1); }
#define FreeString2(C,N)  { FreeNWords2(C,(N)+1); }

#define AllocMerger(C){\
    (C) = (MERGER_RECORD *)H;\
    H += (sizeof(MERGER_RECORD)+sizeof(CELL)-1)/sizeof(CELL);\
    (C)->next = Ref(merger_rec_list);\
    merger_rec_list = (C);\
}


/*************************************************************************
*   Statistics.								 *
*************************************************************************/

#if MRBGC_STATISTICS == 2
#define mrbgc_statistics_deref()		mst_deref++
#define mrbgc_statistics_collect_list()		mst_cslst++
#define mrbgc_statistics_collect_list_fail()	mst_cflst++
#define mrbgc_statistics_reuse_list()		{mst_rslst++; f02total++;}
#define mrbgc_statistics_reuse_list_fail()	mst_rflst++
#define mrbgc_statistics_reuse_in_merger()	{mst_merge++; f02total++;}
#else
#define mrbgc_statistics_deref()
#define mrbgc_statistics_collect_list()
#define mrbgc_statistics_collect_list_fail()
#define mrbgc_statistics_collect_vector(N)
#define mrbgc_statistics_collect_vector_fail(N)
#define mrbgc_statistics_collect_value(N)
#define mrbgc_statistics_collect_in_builtin(N)
#define mrbgc_statistics_reuse_list()
#define mrbgc_statistics_reuse_list_fail()
#define mrbgc_statistics_reuse_vector(N)
#define mrbgc_statistics_reuse_vector_fail(N)
#define mrbgc_statistics_reuse_in_builtin(N)
#define mrbgc_statistics_reuse_in_merger()
#endif


/*************************************************************************
*   Suspension Record.							 *
*************************************************************************/

extern SUSPENSION_RECORD *srec_pool_top;
extern int srec_peek;
#if MRBGC_STATISTICS
extern int srec_total, srec_used;
#endif

#if MRBGC_STATISTICS
#define GetSuspensionRecord(R){\
    if(srec_pool_top == NULL){\
	alloc_suspension_record(1);\
	srec_peek++;\
    }\
    (R) = srec_pool_top;\
    srec_pool_top = SrecOf(srec_pool_top->other);\
    srec_total++; srec_used++;\
}
#else
#define GetSuspensionRecord(R){\
    if(srec_pool_top == NULL){\
	alloc_suspension_record(10);\
	srec_peek += 10;\
    }\
    (R) = srec_pool_top;\
    srec_pool_top = SrecOf(srec_pool_top->other);\
}
#endif

#if MRBGC_STATISTICS
#define GcGetSuspensionRecord(R){\
    (R) = (SUSPENSION_RECORD *)H;\
    H = (CELL *)(((SUSPENSION_RECORD *)H)+1);\
    srec_peek++; srec_total++; srec_used++;\
}
#else
#define GcGetSuspensionRecord(R){\
    (R) = (SUSPENSION_RECORD *)H;\
    H = (CELL *)(((SUSPENSION_RECORD *)H)+1);\
    srec_peek++;\
}
#endif

#if MRBGC_STATISTICS
#define FreeSuspensionRecord(R){\
    register SUSPENSION_RECORD *p = srec_pool_top;\
    srec_pool_top = (R);\
    srec_pool_top->other = Ref(p);\
    srec_used--;\
}
#else
#define FreeSuspensionRecord(R){\
    register SUSPENSION_RECORD *p = srec_pool_top;\
    srec_pool_top = (R);\
    srec_pool_top->other = Ref(p);\
}
#endif

#if MRBGC_STATISTICS
#define SrecUsed() srec_used
#else
#define SrecUsed() srec_peek
#endif

#define SrecUsed2() (srec_peek-count_suspension_record_in_free_list())


/*************************************************************************
*   Goal Record.							 *
*************************************************************************/

extern GOAL_RECORD   *grec08_pool_top;
extern GOAL_RECORD16 *grec16_pool_top;
extern GOAL_RECORD32 *grec32_pool_top;
extern int grec08_peek,	 grec16_peek,  grec32_peek;
#if MRBGC_STATISTICS
extern int grec08_total, grec16_total, grec32_total;
extern int grec08_used,	 grec16_used,  grec32_used;
#endif
extern GOAL_RECORD *goal_rec_list;	   /* for Deadlock Detection */
extern GOAL_RECORD *goal_rec_list_old;	   /* for Deadlock Detection */
extern MERGER_RECORD *merger_rec_list;	   /* for Deadlock Detection */
extern MERGER_RECORD *merger_rec_list_old; /* for Deadlock Detection */

#if MRBGC_STATISTICS
#define GetGoalRecord8(R){\
    if(grec08_pool_top == NULL){\
	alloc_goal_record8(1);\
	grec08_peek++;\
    }\
    (R) = grec08_pool_top;\
    grec08_pool_top = GoalQueuePt(grec08_pool_top);\
    grec08_total++; grec08_used++;\
}
#define GetGoalRecord16(R){\
    if(grec16_pool_top == NULL){\
	alloc_goal_record16(1);\
	grec16_peek++;\
    }\
    (R) = (GOAL_RECORD *)grec16_pool_top;\
    grec16_pool_top = (GOAL_RECORD16 *)GoalQueuePt(grec16_pool_top);\
    grec16_total++; grec16_used++;\
}
#define GetGoalRecord32(R){\
    if(grec32_pool_top == NULL){\
	alloc_goal_record32(1);\
	grec32_peek++;\
    }\
    (R) = (GOAL_RECORD *)grec32_pool_top;\
    grec32_pool_top = (GOAL_RECORD32 *)GoalQueuePt(grec32_pool_top);\
    grec32_total++; grec32_used++;\
}
#else
#define GetGoalRecord8(R){\
    if(grec08_pool_top == NULL){\
	alloc_goal_record8(1);\
	grec08_peek++;\
    }\
    (R) = grec08_pool_top;\
    grec08_pool_top = GoalQueuePt(grec08_pool_top);\
}
#define GetGoalRecord16(R){\
    if(grec16_pool_top == NULL){\
	alloc_goal_record16(1);\
	grec16_peek++;\
    }\
    (R) = (GOAL_RECORD *)grec16_pool_top;\
    grec16_pool_top = (GOAL_RECORD16 *)GoalQueuePt(grec16_pool_top);\
}
#define GetGoalRecord32(R){\
    if(grec32_pool_top == NULL){\
	alloc_goal_record32(1);\
	grec32_peek++;\
    }\
    (R) = (GOAL_RECORD *)grec32_pool_top;\
    grec32_pool_top = (GOAL_RECORD32 *)GoalQueuePt(grec32_pool_top);\
}
#endif
#define GetGoalRecord(R,N){\
    if	   ((N) <=  8){ GetGoalRecord8(R);  }\
    else if((N) <= 16){ GetGoalRecord16(R); }\
    else{		GetGoalRecord32(R); }\
}

#if MRBGC_STATISTICS
#define GcGetGoalRecord8(R){\
    (R) = (GOAL_RECORD *)H;\
    ((GOAL_RECORD *)H)->next = Ref(goal_rec_list);\
    goal_rec_list = (GOAL_RECORD *)H;\
    H = (CELL *)(((GOAL_RECORD *)H)+1);\
    grec08_peek++; grec08_total++; grec08_used++;\
}
#define GcGetGoalRecord16(R){\
    (R) = (GOAL_RECORD *)H;\
    ((GOAL_RECORD *)H)->next = Ref(goal_rec_list);\
    goal_rec_list = (GOAL_RECORD *)H;\
    H = (CELL *)(((GOAL_RECORD16 *)H)+1);\
    grec16_peek++; grec16_total++; grec16_used++;\
}
#define GcGetGoalRecord32(R){\
    (R) = (GOAL_RECORD *)H;\
    ((GOAL_RECORD *)H)->next = Ref(goal_rec_list);\
    goal_rec_list = (GOAL_RECORD *)H;\
    H = (CELL *)(((GOAL_RECORD32 *)H)+1);\
    grec32_peek++; grec32_total++; grec32_used++;\
}
#else
#define GcGetGoalRecord8(R){\
    (R) = (GOAL_RECORD *)H;\
    ((GOAL_RECORD *)H)->next = Ref(goal_rec_list);\
    goal_rec_list = (GOAL_RECORD *)H;\
    H = (CELL *)(((GOAL_RECORD *)H)+1);\
    grec08_peek++;\
}
#define GcGetGoalRecord16(R){\
    (R) = (GOAL_RECORD *)H;\
    ((GOAL_RECORD *)H)->next = Ref(goal_rec_list);\
    goal_rec_list = (GOAL_RECORD *)H;\
    H = (CELL *)(((GOAL_RECORD16 *)H)+1);\
    grec16_peek++;\
}
#define GcGetGoalRecord32(R){\
    (R) = (GOAL_RECORD *)H;\
    ((GOAL_RECORD *)H)->next = Ref(goal_rec_list);\
    goal_rec_list = (GOAL_RECORD *)H;\
    H = (CELL *)(((GOAL_RECORD32 *)H)+1);\
    grec32_peek++;\
}
#endif
#define GcGetGoalRecord(R,N){\
    if	   ((N) <=  8){ GcGetGoalRecord8(R);  }\
    else if((N) <= 16){ GcGetGoalRecord16(R); }\
    else{		GcGetGoalRecord32(R); }\
}

#if MRBGC_STATISTICS
#define FreeGoalRecord8(R){\
    register GOAL_RECORD *p = grec08_pool_top;\
    grec08_pool_top = (R);\
    SetGoalQueuePt2(grec08_pool_top, p);\
    grec08_pool_top->parent = 0;\
    grec08_used--;\
}
#define FreeGoalRecord16(R){\
    register GOAL_RECORD16 *p = grec16_pool_top;\
    grec16_pool_top = (GOAL_RECORD16 *)(R);\
    SetGoalQueuePt2(grec16_pool_top, p);\
    grec16_pool_top->parent = 0;\
    grec16_used--;\
}
#define FreeGoalRecord32(R){\
    register GOAL_RECORD32 *p = grec32_pool_top;\
    grec32_pool_top = (GOAL_RECORD32 *)(R);\
    SetGoalQueuePt2(grec32_pool_top, p);\
    grec32_pool_top->parent = 0;\
    grec32_used--;\
}
#else
#define FreeGoalRecord8(R){\
    register GOAL_RECORD *p = grec08_pool_top;\
    grec08_pool_top = (R);\
    SetGoalQueuePt2(grec08_pool_top, p);\
    grec08_pool_top->parent = 0;\
}
#define FreeGoalRecord16(R){\
    register GOAL_RECORD16 *p = grec16_pool_top;\
    grec16_pool_top = (GOAL_RECORD16 *)(R);\
    SetGoalQueuePt2(grec16_pool_top, p);\
    grec16_pool_top->parent = 0;\
}
#define FreeGoalRecord32(R){\
    register GOAL_RECORD32 *p = grec32_pool_top;\
    grec32_pool_top = (GOAL_RECORD32 *)(R);\
    SetGoalQueuePt2(grec32_pool_top, p);\
    grec32_pool_top->parent = 0;\
}
#endif
#define FreeGoalRecord(R,N){\
    if	   ((N) <=  8){ FreeGoalRecord8(R);  }\
    else if((N) <= 16){ FreeGoalRecord16(R); }\
    else{		FreeGoalRecord32(R); }\
}

#if MRBGC_STATISTICS
#define GrecUsed() (grec08_used+grec16_used+grec32_used)
#else
#define GrecUsed() (grec08_peek+grec16_peek+grec32_peek)
#endif

#define GrecUsed2() ((grec08_peek-count_goal_record8_in_free_list())\
		    +(grec16_peek-count_goal_record16_in_free_list())\
		    +(grec32_peek-count_goal_record32_in_free_list()))


/*************************************************************************
*   Parent (Shoen) Record.						 *
*************************************************************************/

extern PARENT_RECORD *prec_pool_top;
extern int prec_peek;
#if MRBGC_STATISTICS
extern int prec_total, prec_used;
#endif

#if MRBGC_STATISTICS
#define GetParentRecord(R){\
    if(prec_pool_top == NULL){\
	alloc_parent_record(1);\
	prec_peek++;\
    }\
    (R) = prec_pool_top;\
    prec_pool_top = PrecOf(prec_pool_top->parent);\
    prec_total++; prec_used++;\
}
#else
#define GetParentRecord(R){\
    if(prec_pool_top == NULL){\
	alloc_parent_record(10);\
	prec_peek += 10;\
    }\
    (R) = prec_pool_top;\
    prec_pool_top = PrecOf(prec_pool_top->parent);\
}
#endif

#if MRBGC_STATISTICS
#define GcGetParentRecord(R){\
    (R) = (PARENT_RECORD *)H;\
    H = (CELL *)(((PARENT_RECORD *)H)+1);\
    prec_peek++; prec_total++; prec_used++;\
}
#else
#define GcGetParentRecord(R){\
    (R) = (PARENT_RECORD *)H;\
    H = (CELL *)(((PARENT_RECORD *)H)+1);\
    prec_peek++;\
}
#endif

/********* NOT USED **********
#if MRBGC_STATISTICS
#define FreeParentRecord(R){\
    register PARENT_RECORD *p = prec_pool_top;\
    prec_pool_top = (R);\
    prec_pool_top->parent = p;\
    prec_used--;\
}
#else
#define FreeParentRecord(R){\
    register PARENT_RECORD *p = prec_pool_top;\
    prec_pool_top = (R);\
    prec_pool_top->parent = p;\
}
#endif
********** NOT USED *********/

#if MRBGC_STATISTICS
#define PrecUsed() prec_used
#else
#define PrecUsed() prec_peek
#endif

#define PrecUsed2() (prec_peek-count_parent_record_in_free_list())


/*************************************************************************
*   Code area management.						 *
*************************************************************************/

#define CodeSize()	 code_size
#define CodeUsed()	 (C-code1)
#define CodeRest()	 (code1_warn-C)
#define SystemCodeSize() user_code-code_base

#define CheckCode(p)\
    if((p) >= code1_warn){\
	if((p) >= code1_limit){\
	    Error(mesg_code_area_overflow);\
	    exit_pdss(1);\
	}else{\
	    SetCodeGcFlag();\
	}\
    }

#define InCode(P)\
    (((OBJ *)(P)) >= code_base && ((OBJ *)(P)) < user_code_limit)
#define InUserCode(P)\
    (((OBJ *)(P)) >= user_code && ((OBJ *)(P)) < user_code_limit)
#define InActiveCode(P)\
    (((OBJ *)(P)) >= code1 && ((OBJ *)(P)) < code1_limit)

#define IsEmulatedCode(pc)  InCode(pc)
#define IsNativeCode(pc)    (!InCode(pc))
