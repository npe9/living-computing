/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include <sys/types.h>
#include <sys/dir.h>
#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "instr.h"


/*************************************************************************
*   b_create_window(Rname,^Rstt,^Rinterrupt,^Rio)			 *
*************************************************************************/

DCODE dc_create_window()
{
    blt_b_create_window(&R0, &R4, &R5, &R6);
    active_unify(&R1, &R4);
    active_unify(&R2, &R5);
    active_unify(&R3, &R6);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_create_window(name, status, intrup, ioid)
    CELL *name, *status, *intrup, *ioid;
{
    register CELL *x;
    x = name;
    Dereference(x);
    if(Typeof(x) != STRING){
	if(IsRef(x)){
	    body_builtin_suspend(dc_create_window, x,
				 IOOO, name, status, intrup, ioid);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_CREATE_WINDOW,
				   IOOO, name, status, intrup, ioid);
	}
    }else{
	switch(create_window(name, intrup, &Valueof(ioid))){
	  case IOSUB_IO_TABLE_FULL:
	    SetAll(status, INT, IOSUB_IO_TABLE_FULL, MRBOFF);
	    *intrup = const_nil;
	    *ioid = const_nil;
	    return;
	  case IOSUB_SUCCESS:
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	    SetTypeof(ioid, INT); SetMrbof(ioid, MRBOFF);
	    return;
	}
    }
}


/*************************************************************************
*   b_remove_window(Rio,^Rstt)						 *
*************************************************************************/

DCODE dc_remove_window()
{
    blt_b_remove_window(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_remove_window(ioid, status)
    CELL *ioid, *status;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_remove_window, x, IO, ioid, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_REMOVE_WINDOW, IO, ioid, status);
	}
    }else{
	remove_window(Valueof(ioid));
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_show_window(Rio,^Rstt,^Rnewio)					 *
*************************************************************************/

DCODE dc_show_window()
{
    blt_b_show_window(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_show_window(ioid, status, newio)
    CELL *ioid, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_show_window, x, IOO, ioid, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_SHOW_WINDOW, IOO, ioid,status,newio);
	}
    }else{
	show_window(Valueof(ioid));
	*newio = *ioid;
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_hide_window(Rio,^Rstt,^Rnewio)					 *
*************************************************************************/

DCODE dc_hide_window()
{
    blt_b_hide_window(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_hide_window(ioid, status, newio)
    CELL *ioid, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_hide_window, x, IOO, ioid, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_HIDE_WINDOW, IOO, ioid,status,newio);
	}
    }else{
	hide_window(Valueof(ioid));
	*newio = *ioid;
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_create_file(^Rstt,^Rio)						 *
*************************************************************************/

blt_b_create_file(status, ioid)
    CELL *status, *ioid;
{
    switch(create_file(&Valueof(ioid))){
      case IOSUB_IO_TABLE_FULL:
	SetAll(status, INT, IOSUB_IO_TABLE_FULL, MRBOFF);
	*ioid = const_nil;
	return;
      case IOSUB_SUCCESS:
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	SetTypeof(ioid, INT); SetMrbof(ioid, MRBOFF);
	return;
    }
}


/*************************************************************************
*   b_remove_file(Rio,^Rstt)						 *
*************************************************************************/

DCODE dc_remove_file()
{
    blt_b_remove_file(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_remove_file(ioid, status)
    CELL *ioid, *status;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_remove_file, x, IO, ioid, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_REMOVE_FILE, IO, ioid, status);
	}
    }else{
	remove_file(Valueof(ioid));
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_open_file(Rio,Rname,Rmode,^Rstt,^Rnewio)				 *
*************************************************************************/

DCODE dc_open_file()
{
    blt_b_open_file(&R0, &R1, &R2, &R5, &R6);
    active_unify(&R3, &R5);
    active_unify(&R4, &R6);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_open_file(ioid, name, mode, status, newio)
    CELL *ioid, *name, *mode, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = name;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = mode;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(dc_open_file, x,
				 IIIOO, ioid, name, mode, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==ioid ? 1 : (x==name ? 2 : 3)),
				   KL1B_B_OPEN_FILE,
				   IIIOO, ioid, name, mode, status, newio);
	}
    }else{
	switch(open_file(Valueof(ioid), name, Valueof(mode))){
	  case IOSUB_CANNOT_OPEN_FILE:
	    *newio = *ioid;
	    SetAll(status, INT, IOSUB_CANNOT_OPEN_FILE, MRBOFF);
	    return;
	  case IOSUB_SUCCESS:
	    *newio = *ioid;
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	    return;
	}
    }
}


/*************************************************************************
*   b_close_file(Rio,^Rstt,^Rnewio)					 *
*************************************************************************/

DCODE dc_close_file()
{
    blt_b_close_file(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_close_file(ioid, status, newio)
    CELL *ioid, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_close_file, x, IOO, ioid, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_CLOSE_FILE, IOO, ioid,status,newio);
	}
    }else{
	close_file(Valueof(ioid));
	*newio = *ioid;
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_write_char(Rio,Rchar,^Rstt,^Rnewio)				 *
*************************************************************************/

DCODE dc_write_char()
{
    blt_b_write_char(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_write_char(ioid, chr, status, newio)
    CELL *ioid, *chr, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = chr;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(dc_write_char, x,
				 IIOO, ioid, chr, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==ioid ? 1 : 2),
				   KL1B_B_WRITE_CHAR,
				   IIOO, ioid, chr, status, newio);
	}
    }else{
	write_char(Valueof(ioid), Valueof(chr));
	*newio = *ioid;
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_write_line(Rio,Rline,^Rstt,^Rnewio)				 *
*************************************************************************/

DCODE dc_write_line()
{
    blt_b_write_line(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_write_line(ioid, line, status, newio)
    CELL *ioid, *line, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = line;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(dc_write_line, x,
				 IIOO, ioid, line, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==ioid ? 1 : 2),
				   KL1B_B_WRITE_LINE,
				   IIOO, ioid, line, status, newio);
	}
    }else{
	write_line(Valueof(ioid), line);
	if(Mrbof(line) == MRBOFF){
	    FreeString(Objectof(line), StringLengthof(line));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(line)+1);
	}
	*newio = *ioid;
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_write_buffer(Rio,Rbuffer,^Rstt,^Rnewio)				 *
*************************************************************************/

DCODE dc_write_buffer()
{
    blt_b_write_buffer(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_write_buffer(ioid, buffer, status, newio)
    CELL *ioid, *buffer, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = buffer;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(dc_write_buffer, x,
				 IIOO, ioid, buffer, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==ioid ? 1 : 2),
				   KL1B_B_WRITE_BUFFER,
				   IIOO, ioid, buffer, status, newio);
	}
    }else{
	write_buffer(Valueof(ioid), buffer);
	if(Mrbof(buffer) == MRBOFF){
	    FreeString(Objectof(buffer), StringLengthof(buffer));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(buffer)+1);
	}
	*newio = *ioid;
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_write_term(Rio,Rterm,Rlength,Rdepth,^Rstt,^Rnewio)		 *
*************************************************************************/

DCODE dc_write_term()
{
    blt_b_write_term(&R0, &R1, &R2, &R3, &R6, &R7);
    active_unify(&R4, &R6);
    active_unify(&R5, &R7);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_write_term(ioid, term, len, dep, status, newio)
    CELL *ioid, *term, *len, *dep, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = len;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = dep;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(dc_write_term, x,
				 IIIIOO, ioid, term, len, dep, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==ioid ? 1 : (x==len ? 3 : 4)),
				   KL1B_B_WRITE_TERM,
				   IIIIOO, ioid,term,len, dep,status,newio);
	}
    }else{
	write_term(Valueof(ioid), term, Valueof(len), Valueof(dep));
	*newio = *ioid;
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_read_char(Rio,^Rchar,^Rstt,^Rnewio)				 *
*************************************************************************/

DCODE dc_read_char()
{
    blt_b_read_char(&R0, &R4, &R5, &R6);
    active_unify(&R1, &R4);
    active_unify(&R2, &R5);
    active_unify(&R3, &R6);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_read_char(ioid, chr, status, newio)
    CELL *ioid, *chr, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_read_char, x,
				 IOOO, ioid, chr, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_READ_CHAR,
				   IOOO, ioid, chr, status, newio);
	}
    }else{
	int c;
	switch(read_char(Valueof(ioid), &c)){
	  case IOSUB_CONTINUE:
	    body_builtin_suspend(dc_read_char,
				 io_table[Valueof(ioid)].inp_hook,
				 IOOO, ioid, chr, status, newio);
	    return;
	  case IOSUB_END_OF_FILE:
	    *newio = *ioid;
	    *chr = const_nil;
	    SetAll(status, INT, IOSUB_END_OF_FILE, MRBOFF);
	    return;
	  case IOSUB_SUCCESS:
	    *newio = *ioid;
	    SetAll(chr, INT, c, MRBOFF);
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	    return;
	}
    }
}


/*************************************************************************
*   b_read_line(Rio,^Rline,^Rstt,^Rnewio)				 *
*************************************************************************/

DCODE dc_read_line()
{
    blt_b_read_line(&R0, &R4, &R5, &R6);
    active_unify(&R1, &R4);
    active_unify(&R2, &R5);
    active_unify(&R3, &R6);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_read_line(ioid, line, status, newio)
    CELL *ioid, *line, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_read_line, x,
				 IOOO, ioid, line, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_READ_LINE,
				   IOOO, ioid, line, status, newio);
	}
    }else{
	CELL l;
	switch(read_line(Valueof(ioid), &l)){
	  case IOSUB_CONTINUE:
	    body_builtin_suspend(dc_read_line,
				 io_table[Valueof(ioid)].inp_hook,
				 IOOO, ioid, line, status, newio);
	    return;
	  case IOSUB_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_read_line,
			      IOOO, ioid, line, status, newio);
	    return;
	  case IOSUB_END_OF_FILE:
	    *newio = *ioid;
	    *line = l;
	    SetAll(status, INT, IOSUB_END_OF_FILE, MRBOFF);
	    return;
	  case IOSUB_SUCCESS:
	    *newio = *ioid;
	    *line = l;
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	    return;
	}
    }
}


/*************************************************************************
*   b_read_buffer(Rio,Rlength,^Rbuffer,^Rstt,^Rnewio)			 *
*************************************************************************/

DCODE dc_read_buffer()
{
    blt_b_read_buffer(&R0, &R1, &R5, &R6, &R7);
    active_unify(&R2, &R5);
    active_unify(&R3, &R6);
    active_unify(&R4, &R7);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_read_buffer(ioid, len, buffer, status, newio)
    CELL *ioid, *len, *buffer, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = len;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(dc_read_buffer, x,
				 IIOOO, ioid, len, buffer, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==ioid ? 1 : 2),
				   KL1B_B_READ_BUFFER,
				   IIOOO, ioid, len, buffer, status, newio);
	}
    }else{
	CELL b;
	switch(read_buffer(Valueof(ioid), Valueof(len), &b)){
	  case IOSUB_CONTINUE:
	    body_builtin_suspend(dc_read_buffer,
				 io_table[Valueof(ioid)].inp_hook,
				 IIOOO, ioid, len, buffer, status, newio);
	    return;
	  case IOSUB_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_read_buffer,
			      IIOOO, ioid, len, buffer, status, newio);
	    return;
	  case IOSUB_END_OF_FILE:
	    *newio = *ioid;
	    *buffer = b;
	    SetAll(status, INT, IOSUB_END_OF_FILE, MRBOFF);
	    return;
	  case IOSUB_SUCCESS:
	    *newio = *ioid;
	    *buffer = b;
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	    return;
	}
    }
}


/*************************************************************************
*   b_read_token(Rio,^Rtoken,^Rvarnum,^Rstt,^Rnewio)			 *
*************************************************************************/

DCODE dc_read_token()
{
    blt_b_read_token(&R0, &R5, &R6, &R7, &R8);
    active_unify(&R1, &R5);
    active_unify(&R2, &R6);
    active_unify(&R3, &R7);
    active_unify(&R4, &R8);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_read_token(ioid, token, varnum, status, newio)
    CELL *ioid, *token, *varnum, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_read_token, x,
				 IOOOO, ioid, token, varnum, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_READ_TOKEN,
				   IOOOO, ioid, token, varnum, status, newio);
	}
    }else{
	CELL h, t;
	int n;
	switch(read_token(Valueof(ioid), &h, &t, &n)){
	  case IOSUB_CONTINUE:
	    body_builtin_suspend(dc_read_token,
				 io_table[Valueof(ioid)].inp_hook,
				 IIOOO, ioid, &t, varnum, status, newio);
	    *token = h;
	    return;
	  case IOSUB_REQUEST_GC:
	    SetHeapGcFlag();
	    body_builtin_swap(dc_read_token,
			      IIOOO, ioid, &t, varnum, status, newio);
	    *token = h;
	    return;
	  case IOSUB_END_OF_FILE:
	    *newio = *ioid;
	    *token = h;
	    SetAll(varnum, INT, n, MRBOFF);
	    SetAll(status, INT, IOSUB_END_OF_FILE, MRBOFF);
	    return;
	  case IOSUB_EOF_IN_QUOTE:
	    *newio = *ioid;
	    *token = h;
	    SetAll(varnum, INT, n, MRBOFF);
	    SetAll(status, INT, IOSUB_EOF_IN_QUOTE, MRBOFF);
	    return;
	  case IOSUB_SUCCESS:
	    *newio = *ioid;
	    *token = h;
	    SetAll(varnum, INT, n, MRBOFF);
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	    return;
	}
    }
}


/*************************************************************************
*   b_abort_read_command(Rio,^Rstt,^Rnewio)				 *
*************************************************************************/

DCODE dc_abort_read_command()
{
    blt_b_abort_read_command(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_abort_read_command(ioid, status, newio)
    CELL *ioid, *status, *newio;
{
    register CELL *x;
    x = ioid;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_abort_read_command, x,
				 IOO, ioid, status, newio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_ABORT_READ_COMMAND,
				   IOO, ioid, status, newio);
	}
    }else{
	abort_read_command(Valueof(ioid));
	*newio = *ioid;
	SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
    }
}


/*************************************************************************
*   b_test_directory(Rname,^Rstt)					 *
*************************************************************************/

DCODE dc_test_directory()
{
    blt_b_test_directory(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_test_directory(name, status)
    CELL *name, *status;
{
    register CELL *x;
    x = name;
    Dereference(x);
    if(Typeof(x) != STRING){
	if(IsRef(x)){
	    body_builtin_suspend(dc_test_directory, x, IO, name, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_TEST_DIRECTORY, IO, name, status);
	}
    }else{
	CHAR buf1[256], buf2[512];
	DIR *dirp;
	convert_to_c_string(name, buf1, 250);
	if(Mrbof(name) == MRBOFF){
	    FreeString(Objectof(name), StringLengthof(name));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(name)+1);
	}
	if(!(*buf1) || (dirp = opendir(expand_path_name(buf1, buf2))) == NULL){
	    SetAll(status, INT, IOSUB_CANNOT_OPEN_FILE, MRBOFF);
	}else{
	    closedir(dirp);
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	}
    }
}


/*************************************************************************
*   b_directory_pathname(Rname,^Rexname,^Rstt)				 *
*************************************************************************/

DCODE dc_directory_pathname()
{
    blt_b_directory_pathname(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_directory_pathname(name, exname, status)
    CELL *name, *exname, *status;
{
    register CELL *x;
    x = name;
    Dereference(x);
    if(Typeof(x) != STRING){
	if(IsRef(x)){
	    body_builtin_suspend(dc_directory_pathname, x,
				 IOO, name, exname, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_DIRECTORY_PATHNAME,
				   IOO, name, exname, status);
	}
    }else{
	CHAR dir[256], path[512], here[256], *getwd();
	convert_to_c_string(name, dir, 250);
	if(Mrbof(name) == MRBOFF){
	    FreeString(Objectof(name), StringLengthof(name));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(name)+1);
	}
	getwd(here);
	if(!(*dir) || chdir(expand_path_name(dir, path))){
	    SetAll(exname, STRING, convert_to_kl1_string(""), MRBOFF);
	    SetAll(status, INT, IOSUB_CANNOT_OPEN_FILE, MRBOFF);
	}else{
	    getwd(path);
	    chdir(here);
	    SetAll(exname, STRING, convert_to_kl1_string(path), MRBOFF);
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	}
    }
}


/*************************************************************************
*   b_listing_files(Rname,Rwild,^Rlist,^Rstt)				 *
*************************************************************************/

DCODE dc_listing_files()
{
    blt_b_listing_files(&R0, &R1, &R4, &R5);
    active_unify(&R2, &R4);
    active_unify(&R3, &R5);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_listing_files(name, wild, list, status)
    CELL *name, *wild, *list, *status;
{
    register CELL *x;
    x = name;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = wild;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(dc_listing_files, x,
				 IIOO, name, wild, list, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==name ? 1 : 2),
				   KL1B_B_LISTING_FILES,
				   IIOO, name, wild, list, status);
	}
    }else{
	register CELL *p, *q;
	CHAR *dn, bufn[256], bufw[256], ex[512];
	CHAR *wildcard_to_regular_expression(), *re_comp();
	DIR *dirp;
	struct direct *dp, *readdir();
	int st;
	convert_to_c_string(name, bufn, 250);
	convert_to_c_string(wild, bufw, 250);
	if(Mrbof(name) == MRBOFF){
	    FreeString(Objectof(name), StringLengthof(name));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(name)+1);
	}
	if(Mrbof(wild) == MRBOFF){
	    FreeString(Objectof(wild), StringLengthof(wild));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(wild)+1);
	}
	if(!(*bufn) || (dirp = opendir(bufn)) == NULL){
	    st = IOSUB_CANNOT_OPEN_FILE;
	}else{
	    if(*bufw){
		wildcard_to_regular_expression(bufw, ex);
		if(re_comp(ex)){
		    st = IOSUB_CANNOT_OPEN_FILE;
		}else{
		    if(!strcmp(bufn, "/")) *bufn = 0;
		    p = list;
		    st = IOSUB_SUCCESS;
		    while(dp = readdir(dirp)){
			dn = (CHAR *)dp->d_name;
			if(!(*bufw != '.' && *dn == '.') && re_exec(dn)){
			    sprintf(ex, "%s/%s", bufn, dn);
			    AllocCons(q);
			    if(HeapRest() <= 0){
				SetHeapGcFlag();
				st = IOSUB_REQUEST_GC;
				break;
			    }
			    SetAll(p, LIST, q, MRBOFF);
			    SetAll(q, STRING,convert_to_kl1_string(ex),MRBOFF);
			    p = ++q;
			}
		    }
		}
	    }else{
		AllocCons(q);
		if(HeapRest() <= 0){
		    SetHeapGcFlag();
		    st = IOSUB_REQUEST_GC;
		}else{
		    SetAll(list, LIST, q, MRBOFF);
		    SetAll(q, STRING, convert_to_kl1_string(bufn), MRBOFF);
		    p = ++q;
		    st = IOSUB_SUCCESS;
		}
	    }
	    closedir(dirp);
	}
	if(st == IOSUB_SUCCESS){
	    *p = const_nil;
	}else{
	    *list = const_nil;
	}
	SetAll(status, INT, st, MRBOFF);
    }
}


/*************************************************************************
*   b_delete_file(Rname,Rwild,^Rstt)					 *
*************************************************************************/

DCODE dc_delete_files()
{
    blt_b_delete_files(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_delete_files(name, wild, status)
    CELL *name, *wild, *status;
{
    register CELL *x;
    x = name;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = wild;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(dc_delete_files, x,
				 IIO, name, wild, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==name ? 1 : 2),
				   KL1B_B_DELETE_FILES,
				   IIO, name, wild, status);
	}
    }else{
	CHAR *dn, bufn[256], bufw[256], ex[512];
	CHAR *wildcard_to_regular_expression(), *re_comp();
	DIR *dirp, *dirp2;
	struct direct *dp, *readdir();
	int st;
	convert_to_c_string(name, bufn, 250);
	convert_to_c_string(wild, bufw, 250);
	if(Mrbof(name) == MRBOFF){
	    FreeString(Objectof(name), StringLengthof(name));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(name)+1);
	}
	if(Mrbof(wild) == MRBOFF){
	    FreeString(Objectof(wild), StringLengthof(wild));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(wild)+1);
	}
	if(!(*bufn) || (dirp = opendir(bufn)) == NULL){
	    st = IOSUB_CANNOT_OPEN_FILE;
	}else{
	    if(*bufw){
		wildcard_to_regular_expression(bufw, ex);
		if(re_comp(ex)){
		    st = IOSUB_CANNOT_OPEN_FILE;
		}else{
		    st = IOSUB_CANNOT_OPEN_FILE;
		    while(dp = readdir(dirp)){
			dn = (CHAR *)dp->d_name;
			if(!(*bufw != '.' && *dn == '.') && re_exec(dn)){
			    sprintf(ex, "%s/%s", bufn, dn);
			    if(dirp2 = opendir(ex)){
				closedir(dirp2);
			    }else{
				if(!unlink(ex)) st = IOSUB_SUCCESS;
			    }
			}
		    }
		}
	    }else{
		st = IOSUB_CANNOT_OPEN_FILE;
	    }
	    closedir(dirp);
	}
	SetAll(status, INT, st, MRBOFF);
    }
}


/*************************************************************************
*   Wildcard Subroutine							 *
*************************************************************************/

static CHAR *wildcard_to_regular_expression(wildcard, regex)
    CHAR *wildcard, *regex;
{
    CHAR c, *e;
    int pidl;

    e = regex;
    *e++ = '^';
    while(c = *wildcard++){
	switch(c){
	  case '*':
	    *e++ = '.'; *e++ = '*'; break;
	  case '?':
	    *e++ = '.'; break;
	  case '.':
	    *e++ = '\\'; *e++ = '.'; break;
	  case '$':
	    for(pidl = 0, wildcard--; *wildcard=='$'; pidl++, wildcard++);
	    if(pidl == 5) {
		sprintf(e, "%05d", getpid());
		e += 5;
	    }else{
		while(pidl--)
		    *e++ = '$';
	    }
	    break;
	  default:
	    *e++ = c;
	}
    }
    *e++ = '$'; *e = '\0';
    return(regex);
}


/*************************************************************************
*   b_get_time_count(^Rtime,^Rstt)					 *
*************************************************************************/

blt_b_get_time_count(time, status)
    CELL *time, *status;
{
    SetAll(time, INT, get_time_count(), MRBOFF);
    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
}


/*************************************************************************
*   b_on_at(Rtime,^Rdone,^Rstt)						 *
*************************************************************************/

DCODE dc_on_at()
{
    blt_b_on_at(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_on_at(time, done, status)
    CELL *time, *done, *status;
{
    register CELL *x;
    x = time;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_on_at, x, IOO, time, done, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_ON_AT, IOO, time, done, status);
	}
    }else{
	int c = Valueof(time);
	if(c < 0 || c > 5*24*60*60){
	    body_builtin_exception(RANGE_OVERFLOW, 1,
				   KL1B_B_ON_AT, IOO, time, done, status);
	}else{
	    AllocUndef(x);
	    SetAll(done, REF, x, MRBOFF);
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	    set_timer_on_at(c, done);
	}
    }
}


/*************************************************************************
*   b_on_after(Rtime,^Rdone,^Rstt)					 *
*************************************************************************/

DCODE dc_on_after()
{
    blt_b_on_after(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

blt_b_on_after(time, done, status)
    CELL *time, *done, *status;
{
    register CELL *x;
    x = time;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(dc_on_after, x, IOO, time, done, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_ON_AFTER, IOO, time, done, status);
	}
    }else{
	int c = Valueof(time);
	if(c < 0 || c > 5*24*60*60){
	    body_builtin_exception(RANGE_OVERFLOW, 1,
				   KL1B_B_ON_AFTER, IOO, time, done, status);
	}else{
	    AllocUndef(x);
	    SetAll(done, REF, x, MRBOFF);
	    SetAll(status, INT, IOSUB_SUCCESS, MRBOFF);
	    set_timer_on_after(c, done);
	}
    }
}
