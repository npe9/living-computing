/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include <stdio.h>

#define MAX_OF_WINDOW  16
#define MAX_OF_FILE    16
#define IO_BUFSIZ    1024
#define TS_BUFSIZ    1024
#define VT_MEMSIZ    1024
#define VT_HASH	       16

/******* I/O Table & Variable Table *************************************/
typedef struct var_entry{
    struct var_entry *next;
    int		     number;
    CHAR	     name[1];
} VAR_ENTRY;

typedef struct io_backet{
    struct io_backet  *next;	/** Pointer to Next Backet	**/
    int	 status;		/** I/O Status			**/
    FILE *in;			/** UNIX File (IN)		**/
    FILE *out;			/** UNIX File (OUT)		**/

    CHAR *buffer;		/** Buffer for Keyboard Input	**/
    CHAR *buf_p1;		/** Pointer for Buffer IN	**/
    CHAR *buf_p2;		/** Pointer for Buffer OUT	**/
    int	 buf_cc;		/** Char Counter for Buffer	**/
    int	 buf_lc;		/** Line Counter for Buffer	**/
    int	 kb_req;		/** Keyboard Input Request Flag **/

    CHAR *ts_buf;		/** Buffer for Token Scanner	**/
    CHAR *ts_ptr;		/** Pointer for Token Scabber	**/
    int	 ts_siz;		/** Size of Buffer (sc_buf)	**/
    int	 ts_stt;		/** Status of Token Scanner	**/

    int	 var_num;		/** Counter for Variable Number **/
    struct var_entry *var[VT_HASH];	     /** Variable Table **/
    CHAR *vt_mem;		/** Work Memory for Var. Table	**/
    CHAR *vt_ptr;		/** Pointer for "vt_mem"	**/
    int	  vt_siz;		/** Size of Memory for Var Tab  **/

    CELL *inp_hook;		/** Hook for Input Queue	**/
    int	 inp_flag;		/** Input Flag			**/
    CELL *int_hook;		/** Hook for Interrupt Queue	**/
    int	 int_code;		/** Interrupt Code		**/
} IO_BACKET;

extern IO_BACKET  io_table[MAX_OF_WINDOW+MAX_OF_FILE];
extern IO_BACKET  *file_pool;
extern IO_BACKET  *window_pool;
extern int  use_windows;
extern int  current_window;
extern int  print_var_mode;

/******* I/O Status *****************************************************/
#define IO_ACTIVE  0x80
#define IO_READ	   0x01
#define IO_WRITE   0x02

/******* Status of Token Scanner ****************************************/
#define TS_NORMAL  0
#define TS_QATOM   1
#define TS_STRING  2
#define TS_COMMENT 3
#define TS_LINE	   4

/******* Emacs Command **************************************************/
#define EC_END	   0x01
#define EC_WRITE   0x20
#define EC_CREATE  0x30
#define EC_REMOVE  0x40
#define EC_SHOW	   0x50
#define EC_HIDE	   0x60
#define EC_SPECIAL 0x70

/******* Macros for Window, File ****************************************/
#define IsWindow(it)  ((it) < &io_table[MAX_OF_WINDOW])
#define IsFile(it)    ((it) >= &io_table[MAX_OF_WINDOW])
#define CONSOLE	      0

#define GetC(it)\
  (IsWindow(it) ? getc_window(it) : getc((it)->in))
#define UnGetC(chr, it){\
  if(IsWindow(it))\
    ungetc_window(chr,it);\
  else\
    ungetc((chr), (it)->in);\
}

#define ClearTSB(it)\
  (it)->ts_ptr = (it)->ts_buf
#define PutTSB(chr, it){\
  if((it)->ts_ptr >= (it)->ts_buf+(it)->ts_siz)\
    expand_ts_buffer(it);\
  *((it)->ts_ptr)++ = (chr);\
}

#define SelectWindow(wn)\
  if(use_windows && (wn) != current_window){\
    if(current_window >= 0) putchar(EC_END);\
    putchar((wn)|EC_WRITE);\
    current_window = (wn);\
  }
#define CreateWindow(wn, name)\
  if(use_windows){\
    if(current_window >= 0) putchar(EC_END);\
    putchar((wn)|EC_CREATE);\
    printf("%s", name);\
    putchar(EC_END); fflush(stdout);\
    current_window = -1;\
  }
#define RemoveWindow(wn)\
  if(use_windows){\
    if(current_window >= 0) putchar(EC_END);\
    putchar((wn)|EC_REMOVE); fflush(stdout);\
    current_window = -1;\
  }
#define ShowWindow(wn)\
  if(use_windows){\
    if(current_window >= 0) putchar(EC_END);\
    putchar((wn)|EC_SHOW); fflush(stdout);\
    current_window = -1;\
  }
#define HideWindow(wn)\
  if(use_windows){\
    if(current_window >= 0) putchar(EC_END);\
    putchar((wn)|EC_HIDE); fflush(stdout);\
    current_window = -1;\
  }
#define SpecialFunctionToWindow(code)\
  if(use_windows){\
    if(current_window >= 0) putchar(EC_END);\
    putchar((code)|EC_SPECIAL); fflush(stdout);\
    current_window = -1;\
  }

/******** Macros for Console Output *************************************/
#define PrintCons(string)\
  { SelectWindow(CONSOLE); printf("%s", string); }
#define PrintCons1F(format, x1)\
  { SelectWindow(CONSOLE); printf(format, x1); }
#define PrintCons2F(format, x1, x2)\
  { SelectWindow(CONSOLE); printf(format, x1, x2); }
#define PrintCons3F(format, x1, x2, x3)\
  { SelectWindow(CONSOLE); printf(format, x1, x2, x3); }
#define PrintCons4F(format, x1, x2, x3, x4)\
  { SelectWindow(CONSOLE); printf(format, x1, x2, x3, x4); }
#define PrintCons5F(format, x1, x2, x3, x4, x5)\
  { SelectWindow(CONSOLE); printf(format, x1, x2, x3, x4, x5); }
#define PrintCons6F(format, x1, x2, x3, x4, x5, x6)\
  { SelectWindow(CONSOLE); printf(format, x1, x2, x3, x4, x5, x6); }
#define Flush() fflush(stdout)

#define Warning(string)\
  { PrintCons1F("%s\n", string); fflush(stdout); }
#define Warning1F(format, s1)\
  { PrintCons1F(format, s1); putchar('\n'); fflush(stdout); }
#define Warning2F(format, s1, s2)\
  { PrintCons2F(format, s1, s2); putchar('\n'); fflush(stdout); }
#define Warning3F(format, s1, s2, s3)\
  { PrintCons3F(format, s1, s2, s3); putchar('\n'); fflush(stdout); }

#define Error(string)\
  { PrintCons1F("\007%s\n", string); fflush(stdout); }
#define Error1F(format, s1)\
  { putchar('\007'); Warning1F(format, s1); }
#define Error2F(format, s1, s2)\
  { putchar('\007'); Warning2F(format, s1, s2); }
#define Error3F(format, s1, s2, s3)\
  { putchar('\007'); Warning3F(format, s1, s2, s3); }
