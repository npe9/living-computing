/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

/* MODERN: every pointer field of a record is a PREF (port.h), so that a
   record has its 32-bit size on every host.  Records live in the heap,
   and their size is part of the heap accounting that schedules the GC.
   A field is read through the view of its type and written with Ref(). */
#define Ref(P)		pdss_ref(P)
#define CodeOf(R)	((OBJ *)pdss_ptr(R))
#define CellOf(R)	((CELL *)pdss_ptr(R))
#define GrecOf(R)	((GOAL_RECORD *)pdss_ptr(R))
#define SrecOf(R)	((SUSPENSION_RECORD *)pdss_ptr(R))
#define PrecOf(R)	((PARENT_RECORD *)pdss_ptr(R))
#define MrecOf(R)	((MERGER_RECORD *)pdss_ptr(R))

typedef struct goal_record{
    PREF code; PREF_PAD(1)
    PREF pcode; PREF_PAD(2)	/* OBJ * */
    int32_t argn, debug;
    PREF parent; PREF_PAD(3)	/* PARENT_RECORD *: parent shoen */
    PREF next; PREF_PAD(4)	/* GOAL_RECORD *: deadlock detection */
    CELL pt;				/* for ready or suspension queue */
    CELL priority;
    CELL args[8];
} GOAL_RECORD;

typedef struct goal_record16{
    PREF code; PREF_PAD(5)
    PREF pcode; PREF_PAD(6)	/* OBJ * */
    int32_t argn, debug;
    PREF parent; PREF_PAD(7)	/* PARENT_RECORD *: parent shoen */
    PREF next; PREF_PAD(8)	/* GOAL_RECORD *: deadlock detection */
    CELL pt;				/* for ready or suspension queue */
    CELL priority;
    CELL args[16];
} GOAL_RECORD16;

typedef struct goal_record32{
    PREF code; PREF_PAD(9)
    PREF pcode; PREF_PAD(10)	/* OBJ * */
    int32_t argn, debug;
    PREF parent; PREF_PAD(11)	/* PARENT_RECORD *: parent shoen */
    PREF next; PREF_PAD(12)	/* GOAL_RECORD *: deadlock detection */
    CELL pt;				/* for ready or suspension queue */
    CELL priority;
    CELL args[32];
} GOAL_RECORD32;

#define GoalQueuePt(G)\
    Goalof(&((G)->pt))
#define SetGoalQueuePt(G, T, V){\
    SetTypeof(&((G)->pt), T);\
    SetValueof(&((G)->pt), CellValue(V));\
}
#define SetGoalQueuePt2(G, V){\
    SetValueof(&((G)->pt), CellValue(V));\
}
#define SetGoalPriority(G, T, V){\
    SetTypeof(&((G)->priority), T);\
    SetValueof(&((G)->priority), CellValue(V));\
}

/* goal_record.debug */
#define SPIED_GOAL    1
#define NO_TRACE_GOAL 2


typedef struct suspension_record{
    CELL forward, backward;
    PREF suspended; PREF_PAD(13)	/* GOAL_RECORD * */
    PREF other; PREF_PAD(14)	/* SUSPENSION_RECORD * */
} SUSPENSION_RECORD;

#define SetSuspRecForward(S,T,V){\
    SetTypeof(&((S)->forward), T);\
    SetValueof(&((S)->forward), CellValue(V));\
}
#define SetSuspRecBackward(S,T,V){\
    SetTypeof(&((S)->backward), T);\
    SetValueof(&((S)->backward), CellValue(V));\
}


typedef struct parent_record{
    int32_t status;
    int32_t number_of_children;
    int32_t number_of_children2;	/* for parent termination at GC */
    int32_t reduction_arrowed_max;	/* for resource management */
    int32_t reduction_left;		/* for resource management */
    int32_t total_of_reduction;		/* for statistics */
    uint32_t id;
    uint32_t priority_max, priority_min;
    uint32_t tag;
    PREF parent; PREF_PAD(15)
    PREF left_son; PREF_PAD(16)
    PREF right_son; PREF_PAD(17)	/* PARENT_RECORD * */
    PREF left_brother; PREF_PAD(18)
    PREF right_brother; PREF_PAD(19)	/* PARENT_RECORD * */
    CELL queue;
    CELL report;
} PARENT_RECORD;

#define READY	 0x00
#define ABORTED	 0xFF
#define SUSP_P	 0x01		/* was suspended by parent Sho-en */
#define SUSP_D	 0x02		/* was suspended via control stream */
#define SUSP_PD	 0x03
#define RESOURCE_EXHAUSTED	0x10
#define	RESOURCE_REQUEST	0x20 /* resuest from KO Sho-en */

#define IsParentReady(P)	  ((P)->status == READY)
#define IsParentSuspended(P)	  ((P)->status>READY && !IsParentAborted(P))
#define IsParentAborted(P)	  ((P)->status == ABORTED)
#define	IsChildRequestResource(P) ((P)->status & RESOURCE_REQUEST)
#define	IsResourceExhausted(P)	  ((P)->status & RESOURCE_EXHAUSTED)


/*************************************************************************
*   Cache / Decache							 *
*************************************************************************/

#define SaveArgs(ARGN, ARGS, REGS){\
    register int i = ARGN;\
    while(i--){\
	ARGS[i] = REGS[i];\
    }\
}

#define CacheGoal(GOAL){\
    register int i;\
    register CELL *args;\
    PC = CodeOf((GOAL)->code);\
    number_of_argument = i = (GOAL)->argn;\
    args = (GOAL)->args;\
    while(i--){\
	regs[i] = args[i];\
    }\
    current_predicate = PC;\
    current_predicate2 = CodeOf((GOAL)->pcode);\
    logical_priority = (GOAL)->priority.value;\
    goal_debug_status = (GOAL)->debug;\
}

#define DecacheGoal(GOAL, CODE){\
    register int i;\
    register CELL *args;\
    i = number_of_argument;\
    GetGoalRecord(GOAL, i);\
    (GOAL)->code = Ref(CODE);\
    (GOAL)->pcode = Ref(current_predicate2);\
    (GOAL)->argn = i;\
    (GOAL)->parent = Ref(parent);\
    args = (GOAL)->args;\
    while(i--){\
	args[i] = regs[i];\
    }\
    SetGoalPriority((GOAL), INT, logical_priority);\
    (GOAL)->debug = goal_debug_status;\
}

#define DecacheParent(){\
    if(parent != NULL){\
	parent->number_of_children = number_of_children;\
	parent->total_of_reduction +=\
	    (parent->reduction_left - reduction_left);\
	parent->reduction_left = reduction_left;\
	parent = NULL;\
    }\
}

#define CacheParent(CURRENT_PARENT){\
    parent = (CURRENT_PARENT);\
    if(parent){\
	reduction_left = parent->reduction_left;\
	number_of_children = parent->number_of_children;\
    }\
}

#define CacheParent2(CURRENT_PARENT){\
    if(parent != NULL){\
	parent->number_of_children = number_of_children;\
	parent->total_of_reduction +=\
	    (parent->reduction_left - reduction_left);\
	parent->reduction_left = reduction_left;\
    }\
    parent = (CURRENT_PARENT);\
    if(parent){\
	reduction_left = parent->reduction_left;\
	number_of_children = parent->number_of_children;\
    }\
}
