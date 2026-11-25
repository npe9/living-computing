/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

typedef struct goal_record{
    OBJ	 *code, *pcode;
    int	 argn, debug;
    struct parent_record *parent;	/* pointer to parent shoen */
    struct goal_record *next;		/* for deadlock detection */
    CELL pt;				/* for ready or suspension queue */
    CELL priority;
    CELL args[8];
} GOAL_RECORD;

typedef struct goal_record16{
    OBJ	 *code, *pcode;
    int	 argn, debug;
    struct parent_record *parent;	/* pointer to parent shoen */
    struct goal_record16 *next;		/* for deadlock detection */
    CELL pt;				/* for ready or suspension queue */
    CELL priority;
    CELL args[16];
} GOAL_RECORD16;

typedef struct goal_record32{
    OBJ	 *code, *pcode;
    int	 argn, debug;
    struct parent_record *parent;	/* pointer to parent shoen */
    struct goal_record32 *next;		/* for deadlock detection */
    CELL pt;				/* for ready or suspension queue */
    CELL priority;
    CELL args[32];
} GOAL_RECORD32;

#define GoalQueuePt(G)\
    Goalof(&((G)->pt))
#define SetGoalQueuePt(G, T, V){\
    SetTypeof(&((G)->pt), T);\
    SetValueof(&((G)->pt), (int)(V));\
}
#define SetGoalQueuePt2(G, V){\
    SetValueof(&((G)->pt), (int)(V));\
}
#define SetGoalPriority(G, T, V){\
    SetTypeof(&((G)->priority), T);\
    SetValueof(&((G)->priority), (int)(V));\
}

/* goal_record.debug */
#define SPIED_GOAL    1
#define NO_TRACE_GOAL 2


typedef struct suspension_record{
    CELL forward, backward;
    struct goal_record *suspended;
    struct suspension_record *other;
} SUSPENSION_RECORD;

#define SetSuspRecForward(S,T,V){\
    SetTypeof(&((S)->forward), T);\
    SetValueof(&((S)->forward), (int)(V));\
}
#define SetSuspRecBackward(S,T,V){\
    SetTypeof(&((S)->backward), T);\
    SetValueof(&((S)->backward), (int)(V));\
}


typedef struct parent_record{
    int	 status;
    int	 number_of_children;
    int	 number_of_children2;	/* for parent termination at GC */
    int	 reduction_arrowed_max;	/* for resource management */
    int	 reduction_left;	/* for resource management */
    int	 total_of_reduction;	/* for statistics */
    unsigned int id;
    unsigned int priority_max, priority_min;
    unsigned int tag;
    struct parent_record *parent, *left_son, *right_son;
    struct parent_record *left_brother, *right_brother;
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
    PC = (GOAL)->code;\
    number_of_argument = i = (GOAL)->argn;\
    args = (GOAL)->args;\
    while(i--){\
	regs[i] = args[i];\
    }\
    current_predicate = PC;\
    current_predicate2 = (GOAL)->pcode;\
    logical_priority = (GOAL)->priority.value;\
    goal_debug_status = (GOAL)->debug;\
}

#define DecacheGoal(GOAL, CODE){\
    register int i;\
    register CELL *args;\
    i = number_of_argument;\
    GetGoalRecord(GOAL, i);\
    (GOAL)->code = (CODE);\
    (GOAL)->pcode = current_predicate2;\
    (GOAL)->argn = i;\
    (GOAL)->parent = parent;\
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
