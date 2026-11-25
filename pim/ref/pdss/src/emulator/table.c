/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
**************************************************************************

  General Purpose (?) Name Table Lookup Subroutine Package.
  The user of this package should define the following macros:

    TABLE_NAME:
	Name of the variable which represents the table.
    ENTRY_TYPE_NAME:
	Name of the type which represents the table entries.
    DATA_TYPE:
	The type of the data to be stored into the table.
    TABLE_SIZE:
	The size of the hash table.
    INIT_ROUTINE_NAME:
	Name of the table initiation routine.
    LOOKUP_ROUTINE_NAME:
	Name of the table lookup routine.
	Checks out non-existent entry.
    ENTRY_ROUTINE_NAME:
	Name of the item entry routine.
	Checks out double entry.

  The following macros are optional.  Routines are defined only when
  these macros are defined:

    DELETION_ROUTINE_NAME:
	Name of the item deletion routine.
	Checks out non-existent entry.
    UPDATE_ROUTINE_NAME:
	Name of the item update routine.
	Checks out non-existent entry.
    HASH_COEFFICIENT:
	Coefficient used to compute hash value from strings.
	Defaults to 37.
    MALLOC_ROUTINE_NAME:
	Name of the routine to allocate memory for the table.
	Defaults to "malloc".
    MALLOC_FAILURE_ROUTINE1:
    MALLOC_FAILURE_ROUTINE2:
	The routine called if memory allocation routine failed.
	MALLOC_FAILURE_ROUTINE1 is used in the table initiation routine.
	MALLOC_FAILURE_ROUTINE2 is used in the table lookup routine.
    MFREE_ROUTINE_NAME:
	Name of the routine to free memory for the table.
	Defaults to "free".

*******************************************************************/

#include <string.h>

struct ENTRY_TYPE_NAME{
    struct ENTRY_TYPE_NAME *next;   /* link for hash bucket */
    unsigned char *key;		    /* name to be used as the key */
    DATA_TYPE data;		    /* data associated with the key */
};

struct TABLE_NAME{
    struct ENTRY_TYPE_NAME *table[TABLE_SIZE];
    struct ENTRY_TYPE_NAME *entry_pool;
    int entry_pool_count;
#ifdef DELETION_ROUTINE_NAME
    struct ENTRY_TYPE_NAME *entry_list;
#endif
} TABLE_NAME;

#ifndef HASH_COEFFICIENT
#define HASH_COEFFICIENT 37
#endif

#ifndef MALLOC_ROUTINE_NAME
#define MALLOC_ROUTINE_NAME malloc
#endif

#ifndef MFREE_ROUTINE_NAME
#define MFREE_ROUTINE_NAME free
#endif

#if TABLE_SIZE==01 || TABLE_SIZE==02 || TABLE_SIZE==04 ||\
    TABLE_SIZE==010 || TABLE_SIZE==020 || TABLE_SIZE==040 ||\
    TABLE_SIZE==0100 || TABLE_SIZE==0200 || TABLE_SIZE==0400 ||\
    TABLE_SIZE==01000 || TABLE_SIZE==02000 || TABLE_SIZE==04000 ||\
    TABLE_SIZE==010000 || TABLE_SIZE==020000 || TABLE_SIZE==040000 ||\
    TABLE_SIZE==0100000 || TABLE_SIZE==0200000 || TABLE_SIZE==0400000 ||\
    TABLE_SIZE==01000000 || TABLE_SIZE==02000000 || TABLE_SIZE==04000000
#define HASH_MASK(v)	((v) & ((TABLE_SIZE)-1))
#else
#define HASH_MASK(v)	((v) % (TABLE_SIZE))
#endif

#define hash_name(name, value)\
{\
    register unsigned char *p = (name);\
    value = 0;\
    while(*p) value = HASH_MASK(HASH_COEFFICIENT * value + *p++);\
}

int INIT_ROUTINE_NAME(void)
{
    register struct ENTRY_TYPE_NAME **p = TABLE_NAME.table;
    while(p != &TABLE_NAME.table[TABLE_SIZE]) *p++ = 0;
    TABLE_NAME.entry_pool = (struct ENTRY_TYPE_NAME *)
	MALLOC_ROUTINE_NAME(sizeof(struct ENTRY_TYPE_NAME) * TABLE_SIZE);
#ifdef MALLOC_FAILURE_ROUTINE1
    if(TABLE_NAME.entry_pool == NULL) MALLOC_FAILURE_ROUTINE1;
#endif
    TABLE_NAME.entry_pool_count = TABLE_SIZE;
#ifdef DELETION_ROUTINE_NAME
    TABLE_NAME.entry_list = NULL;
#endif
    return 0;
}

unsigned int LOOKUP_ROUTINE_NAME(unsigned char *key, DATA_TYPE *value)
{
    register unsigned int hv;
    register struct ENTRY_TYPE_NAME *p;
    hash_name(key, hv);
    p = TABLE_NAME.table[hv];
    while(p){
	if(!strcmp(key, p->key)){
	    *value = p->data;
	    return 0;  /** Found **/
	}
	p = p->next;
    }
    return 1;	   /** Not Found **/
}

unsigned int ENTRY_ROUTINE_NAME(unsigned char *key, DATA_TYPE *value)
{
    register unsigned int hv;
    register struct ENTRY_TYPE_NAME *p;
    hash_name(key, hv);
    p = TABLE_NAME.table[hv];
    while (p) {
	if (!strcmp(key, p->key)) return 1;   /** Double Definition **/
	p = p->next;
    }
#ifdef DELETION_ROUTINE_NAME
    if(TABLE_NAME.entry_list == NULL){
#endif
	if(TABLE_NAME.entry_pool_count <= 0){
	    TABLE_NAME.entry_pool = (struct ENTRY_TYPE_NAME *)
		MALLOC_ROUTINE_NAME(sizeof(struct ENTRY_TYPE_NAME)
				    * TABLE_SIZE);
#ifdef MALLOC_FAILURE_ROUTINE2
	    if(TABLE_NAME.entry_pool == NULL) MALLOC_FAILURE_ROUTINE2;
#endif
	    TABLE_NAME.entry_pool_count = TABLE_SIZE;
	}
	p = &TABLE_NAME.entry_pool[--TABLE_NAME.entry_pool_count];
#ifdef DELETION_ROUTINE_NAME
    }else{
	p = TABLE_NAME.entry_list;
	TABLE_NAME.entry_list = p->next;
    }
#endif
    p->next = TABLE_NAME.table[hv];
    p->key = key;
    p->data = *value;
    TABLE_NAME.table[hv] = p;
    return 0;
}

#ifdef DELETION_ROUTINE_NAME
unsigned int DELETION_ROUTINE_NAME(unsigned char *key)
{
    register unsigned int hv;
    register struct ENTRY_TYPE_NAME **pp;
    hash_name(key, hv);
    pp = &TABLE_NAME.table[hv];
    while (*pp) {
	if (!strcmp(key, (*pp)->key)) {
	    register struct ENTRY_TYPE_NAME *p = *pp;
	    *pp = p->next;
	    p->next = TABLE_NAME.entry_list;
	    TABLE_NAME.entry_list = p;
	    return 0;	/** Found & Deleted **/
	}
	pp = &(*pp)->next;
    }
    return 1;		      /** Not Found **/
}
#undef DELETION_ROUTINE_NAME
#endif

#ifdef UPDATE_ROUTINE_NAME
unsigned int UPDATE_ROUTINE_NAME(unsigned char *key, DATA_TYPE *value)
{
    register unsigned int hv;
    register struct ENTRY_TYPE_NAME *p;
    hash_name(key, hv);
    p = TABLE_NAME.table[hv];
    while (p) {
	if (!strcmp(key, p->key)) {
	    p->data = *value;
	    return 0;	/** Found & Updated **/
	}
	p = p->next;
    }
    return 1;		      /** Not Found **/
}
#undef UPDATE_ROUTINE_NAME
#endif

#undef TABLE_NAME
#undef ENTRY_TYPE_NAME
#undef DATA_TYPE
#undef TABLE_SIZE
#undef INIT_ROUTINE_NAME
#undef LOOKUP_ROUTINE_NAME
#undef ENTRY_ROUTINE_NAME
#undef HASH_COEFFICIENT
#undef HASH_MASK
#undef MALLOC_ROUTINE_NAME
#undef MALLOC_FAILURE_ROUTINE1
#undef MALLOC_FAILURE_ROUTINE2
#undef MFREE_ROUTINE_NAME
