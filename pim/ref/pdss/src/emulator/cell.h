/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

/* MODERN: the cell is 8 bytes on every host (port.h); a pointer value
   is a PREF, converted by the accessors below. */
typedef struct cell{
    uint16_t type;
    uint16_t mrb;
    int32_t  value;
} CELL;
typedef CELL *CELLP;

#define Typeof(X)	((X)->type)
#define SetTypeof(X,T)	(X)->type = (T)
#define Valueof(X)	((X)->value)
#define SetValueof(X,V)	(X)->value = (V)
#define Mrbof(X)	((X)->mrb)
#define SetMrbof(X,M)	(X)->mrb = (M)
#define SetAll(X,T,V,M) \
	    { SetTypeof(X,T); SetMrbof(X,M); SetValueof(X,CellValue(V)); }

#define Pointerof(X)	 pdss_ptr((PREF)Valueof(X))
#define Objectof(X)	 ((CELL *)Pointerof(X))
#define SetObjectof(X,V) SetValueof(X, (int32_t)pdss_ref(V))
#define Goalof(X)	 ((GOAL_RECORD *)Pointerof(X))
#define SetGoalof(X,V)	 SetValueof(X, (int32_t)pdss_ref(V))
#define Suspof(X)	 ((SUSPENSION_RECORD *)Pointerof(X))
#define SetSuspof(X,V)	 SetValueof(X, (int32_t)pdss_ref(V))
#define Shoenof(X)	 ((PARENT_RECORD *)Pointerof(X))
#define SetShoenof(X,V)	 SetValueof(X, (int32_t)pdss_ref(V))


/*************************************************************************
*   Type								 *
*************************************************************************/

typedef unsigned int TYPE;

#define UNDEF	0x01
#define HOOK	0x02
#define MHOOK	0x03
#define MGHOK	0x04
#define REF	0x05
#define ATOM	0x06
#define INT	0x07
#define FLOAT	0x08
#define LIST	0x09
#define VECTOR	0x0A
#define STRING	0x0B
#define DESC	0x0C
#define NUE	0x0D
#define SHOEN	0x0E

#define IsRef(C)	(Typeof(C) == REF)
#define IsUnbound(C)	(Typeof(C) < REF)

#define IntOverflow(x)	((x) < -2147483648.0 || (x) > 2147483647.0)
#define IntOverflowP(x) ((x) > 2147483647.0)
#define IntOverflowM(x) ((x) > 2147483648.0)
#define IntOverflowU(x) ((x) > 4294967295.0)


/*************************************************************************
*   MRB									 *
*************************************************************************/

typedef unsigned int MRB;

#define MRBOFF	NO
#define MRBON	YES


/*************************************************************************
*   Structure								 *
*************************************************************************/

#define Carof(LP)	Objectof(LP)
#define Cdrof(LP)	(Objectof(LP)+1)
/*
    +------+------+	 +-------------+
    | LIST |   --------->|    C A R    |
    +------+------+	 +-------------+
			 |    C D R    |
			 +-------------+
*/

#define VectorElementof(VP,IX)	(Objectof(VP)+(IX)+1)
#define VectorLengthof(C)	(Valueof(Objectof(C)) & 0xFFFFFF)
/*
				  8bits	   24bits
    +------+------+	 +------+------+------------+
    |VECTOR|   --------->| DESC | 0x00 |   Length   |
    +------+------+	 +------+------+------------+ ---
			 |	 Element   #0	    |  ^
			 +--------------------------+  |
			 |	 Element   #1	    |  |Length
			 +--------------------------+  |
			 |	     . . .	    |  v
			 +--------------------------+ ---
*/

#define StringLengthof(C)	(Valueof(Objectof(C)) & 0xFFFFFF)
#define StringTypeof(C)		((Valueof(Objectof(C)) >> 24) & 0xFF)
/*
				  8bits	   24bits
    +------+------+	 +------+------+------------+
    |STRING|   --------->| DESC | Type |   Length   |
    +------+------+	 +------+------+------------+ ---
			 |	 Elements  #0	    |  ^
			 +--------------------------+  |
			 |	 Elements  #1	    |  |Length
			 +--------------------------+  |
			 |	     . . .	    |  v
			 +--------------------------+ ---
*/

#define NueLengthof(C)	   (Valueof(Objectof(C)) & 0xFFFFFF)
#define NueCellsof(C)	   ((Valueof(Objectof(C)) >> 24) & 0xFF)
/*
				  8bits	   24bits
    +------+------+	 +------+------+------------+
    |  NUE |   --------->| DESC | Cells|   Length   |
    +------+------+	 +------+------+------------+ ----------
			 |	 Elements  #0	    |	      ^
			 +--------------------------+ ---     |
			 |	 Elements  #1	    |  ^      |
			 +--------------------------+  |      |
			 |	     . . .	    |  |Cells |Length
			 +--------------------------+  |      |
			 |	 Elements  #N	    |  v      |
			 +--------------------------+ ---     |
			 |	    W O R K	    |	      |
			 |			    |	      v
			 +--------------------------+ ----------
*/

typedef struct merger_record{
    CELL output;			/* merger output */
    uint32_t count;			/* number of merger input */
    uint32_t priority;			/* priority of merger */
    PREF parent; PREF_PAD(1)		/* struct parent_record *: parent shoen */
    PREF pcode; PREF_PAD(2)		/* OBJ *: predicate what create merger */
    PREF input; PREF_PAD(3)		/* CELL *: for deadlock detection */
    PREF next; PREF_PAD(4)		/* struct merger_record *: deadlock det. */
} MERGER_RECORD;

#define Mergerof(X)		  ((MERGER_RECORD *)Pointerof(X))
#define SetMergerof(X,MG)	  SetValueof(X, (int32_t)pdss_ref(MG))
#define MergerTailof(MG)	  (&(Mergerof(MG)->output))
#define MergerRefCountof(MG)	  (Mergerof(MG)->count)
#define SetMergerRefCountof(MG,I) { Mergerof(MG)->count = (I); }
/*
			  MG		       MERGER_RECORD
    +------+------+	 +------+------+      +-------------+
    |  REF |   --------->| MGHOK|   --------->| Merger-Tail |
    +------+------+	 +------+------+      +-------------+
					      |Counter (int)|
					      +-------------+
					      |	    ...	    |
					      |		    |
					      +-------------+
*/
