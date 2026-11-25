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

#define SetSrecGCflag(p, new)   { (p)->other = Ref((new)); }
#define GetCopiedSrec(p)        (SrecOf((p)->other))
#define IsSrecCopied(p)	        InActiveHeap(SrecOf((p)->other))
#define IsNotSrecCopied(p)      (!IsSrecCopied(p))

#define SetGrecGCflag(g)        { (g)->code = 0; }
#define IsGrecCopied(g)	        (CodeOf((g)->code) == NULL)
#define IsNotGrecCopied(g)      (CodeOf((g)->code) != NULL)

#define SetPrecGCflag(p, new)   { (p)->parent = Ref((new)); }
#define GetCopiedPrec(p)        (PrecOf((p)->parent))
#define IsPrecCopied(p)	        InActiveHeap(PrecOf((p)->parent))
#define IsNotPrecCopied(p)      (!IsPrecCopied(p))


/* MODERN: the forwarding address is a PREF in the module's 32-bit size
   field (the original stored a 32-bit pointer there). */
#define IsCodeCopied(mtop)\
    (pdss_get16((mtop)+MODULE_ENTRY_TABLE_SIZE) == 0)
#define IsNotCodeCopied(mtop)  (!IsCodeCopied(mtop))
#define GetNewAddress(mtop)\
    CodeOf(pdss_getu32((mtop)+MODULE_CODE_SIZE))
#define SetCodeGCinfo(old, new)\
    { pdss_put32((old)+MODULE_CODE_SIZE, Ref(new));\
      pdss_put16((old)+MODULE_ENTRY_TABLE_SIZE, 0); }


#define GcProcedure(code)\
    (gc_code ? gc_predicate(code) : (code))
#define GcConstInCode(cell)\
    (gc_code ? gc_cell_in_constant_section(cell) : (cell))


#define IsConstInCode(p)       (!InHeap(p))
#define IsConstInNativeCode(p) (!InCode((OBJ *)(p)))
