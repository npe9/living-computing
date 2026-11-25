/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

extern int gc_code;

#define COPIED 0x0F
#define SetOldNewPointer1(X,Y) \
	   { SetTypeof(X,COPIED); SetMrbof(X,MRBOFF); SetObjectof(X,Y); }
#define SetOldNewPointer2(X,Y)  { SetMrbof(X,MRBON); SetObjectof(X,Y); }
#define MarkOldNewPointer(X)    { SetMrbof(X,MRBON); }
#define IsCopied(p)	        (Typeof(p) == COPIED)
#define IsNotCopied(p)	        (!IsCopied(p))

#define SetSrecGCflag(p, new)   { (p)->other = (new); }
#define GetCopiedSrec(p)        ((p)->other)
#define IsSrecCopied(p)	        InActiveHeap((p)->other)
#define IsNotSrecCopied(p)      (!IsSrecCopied(p))

#define SetGrecGCflag(g)        { (g)->code = NULL; }
#define IsGrecCopied(g)	        ((g)->code == NULL)
#define IsNotGrecCopied(g)      ((g)->code != NULL)

#define SetPrecGCflag(p, new)   { (p)->parent = (new); }
#define GetCopiedPrec(p)        ((p)->parent)
#define IsPrecCopied(p)	        InActiveHeap((p)->parent)
#define IsNotPrecCopied(p)      (!IsPrecCopied(p))


#define IsCodeCopied(mtop)\
    (*((short *)((mtop)+MODULE_ENTRY_TABLE_SIZE)) == 0)
#define IsNotCodeCopied(mtop)  (!IsCodeCopied(mtop))
#define GetNewAddress(mtop)\
    (*((OBJ **)((mtop)+MODULE_CODE_SIZE)))
#define SetCodeGCinfo(old, new)\
    { *((OBJ **)((old)+MODULE_CODE_SIZE)) = (new);\
      *((short *)((old)+MODULE_ENTRY_TABLE_SIZE)) = 0; }


#define GcProcedure(code)\
    (gc_code ? gc_predicate(code) : (code))
#define GcConstInCode(cell)\
    (gc_code ? gc_cell_in_constant_section(cell) : (cell))


#define IsConstInCode(p)       (!InHeap(p))
#define IsConstInNativeCode(p) (!InCode((OBJ *)(p)))
