/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include  <signal.h>
#include  "pdss.h"
#include  "memory.h"
#include  "io.h"
/* PORT: forward declarations */
static int keyboard_to_buffer();
static int keyboard_eof_to_buffer();
static int keyboard_interrupt();
static int keyboard_interrupt_without_emacs();


#ifndef sigmask
#define sigmask(m) (1 << ((m)-1))
#endif

IO_BACKET  io_table[MAX_OF_WINDOW+MAX_OF_FILE];
IO_BACKET  *file_pool;
IO_BACKET  *window_pool;
int  use_windows;
int  current_window;
int  print_var_mode;


/*************************************************************************
*   Initialize I/O.							 *
*************************************************************************/

initialize_io()
{
    register IO_BACKET	*it, **nx;
    register int i, j;
    register CHAR *buf;
    int	 keyboard_interrupt();
    int	 keyboard_interrupt_without_emacs();
    CHAR *malloc();

    current_window = -1;
    use_windows = option_use_windows;

    /**** Console ****/
    it = &io_table[0];
    it->status = 0;
    it->kb_req = 0;
    it++;

    /**** Windows ****/
    nx = &window_pool;
    for(i=1; i<MAX_OF_WINDOW; i++,it++){
	*nx = it;
	nx = &(it->next);
	it->status = 0;
	it->in	   = stdin;
	it->out	   = stdout;
	if(use_windows){
	    buf = malloc(IO_BUFSIZ);
	    if(buf == NULL){
		Error("Not Enough Memory (malloc failure) -- Aborted.");
		exit_pdss(1);
	    }
	    it->buffer = buf;
	    it->buf_p1 = buf;
	    it->buf_p2 = buf;
	    it->buf_cc = 0;
	    it->buf_lc = 0;
	    it->kb_req = 0;
	}
	buf = malloc(TS_BUFSIZ);
	if(buf == NULL){
	    Error("Not Enough Memory (malloc failure) -- Aborted.");
	    exit_pdss(1);
	}
	it->ts_buf = buf;
	it->ts_ptr = buf;
	it->ts_siz = TS_BUFSIZ;
	it->ts_stt = TS_NORMAL;
	it->var_num = 0;
	for(j=0; j<VT_HASH; j++) it->var[j] = NULL;
	buf = malloc(VT_MEMSIZ);
	if(buf == NULL){
	    Error("Not Enough Memory (malloc failure) -- Aborted.");
	    exit_pdss(1);
	}
	it->vt_mem = buf;
	it->vt_ptr = buf;
	it->vt_siz = VT_MEMSIZ;
    }
    *nx = NULL;

    /**** Files ****/
    nx = &file_pool;
    buf = malloc(TS_BUFSIZ);
    if(buf == NULL){
	Error("Not Enough Memory (malloc failure) -- Aborted.");
	exit_pdss(1);
    }
    for(i=0; i<MAX_OF_FILE; i++,it++){
	*nx = it;
	nx = &(it->next);
	it->status = 0;
	it->ts_buf = buf;
	it->ts_ptr = buf;
	it->ts_siz = TS_BUFSIZ;
	it->ts_stt = TS_NORMAL;
	it->var_num = 0;
	for(j=0; j<VT_HASH; j++) it->var[j] = NULL;
	buf = malloc(VT_MEMSIZ);
	if(buf == NULL){
	    Error("Not Enough Memory (malloc failure) -- Aborted.");
	    exit_pdss(1);
	}
	it->vt_mem = buf;
	it->vt_ptr = buf;
	it->vt_siz = VT_MEMSIZ;
    }
    *nx = NULL;

    if(use_windows){
	signal(SIGINT,	keyboard_interrupt);
	signal(SIGQUIT, abort_pdss);
	signal(SIGTERM, abort_pdss);
    }else{
	signal(SIGINT,	keyboard_interrupt_without_emacs);
	signal(SIGQUIT, abort_pdss);
	signal(SIGTERM, abort_pdss);
	signal(SIGTSTP, stop_pdss);
    }
}


/*************************************************************************
*   Signal Handling.							 *
*************************************************************************/

io_ctrl_when_exit()
{
    signal(SIGINT,  SIG_IGN);
    signal(SIGQUIT, SIG_IGN);
    signal(SIGTERM, SIG_IGN);
    signal(SIGTSTP, SIG_IGN);
}

io_ctrl_when_stop()
{
    return;
}

io_ctrl_when_resume()
{
    signal(SIGTSTP, stop_pdss);
}


/*************************************************************************
*   Read Console.							 *
*************************************************************************/

int read_console(prompt, line, n)
    CHAR *prompt, *line;
    int	 n;
{
    register int  i, ch;

    SpecialFunctionToWindow(2);
    PrintCons1F("%s", prompt);
    request_console();
    i = 0; n--;
    while((ch = getchar()) != '\n'){
	if(ch == EOF) break;
	if(i < n) line[i++] = ch;
    }
    line[i] = 0;
    SpecialFunctionToWindow(0);
    SelectWindow(CONSOLE);
    return(ch==EOF ? -1: i);
}


/*************************************************************************
*   Keyboard Support.							 *
*************************************************************************/

int getc_window(it)
    register IO_BACKET	*it;
{
    register int  chr;

    if(use_windows){
	if(it->buf_cc > 0){
	    if(*(it->buf_p2)==(EOF&0xFF)) return(EOF);
	    chr = *(it->buf_p2)++;
	    if(it->buf_p2 >= &(it->buffer[IO_BUFSIZ]))
		it->buf_p2 = &(it->buffer[0]);
	    it->buf_cc--;
	    if(chr == '\n') it->buf_lc--;
	    return(chr);
	}else{
	    Error("Getc from empty keyboard buffer.");
	    return(EOF);
	}
    }else{
	if(it->buf_cc != EOF){
	    chr = it->buf_cc;
	    it->buf_cc = EOF;
	    return(chr);
	}
	if(it->buf_lc){
	    chr = getc((it)->in);
	    if(chr == EOF){
		it->buf_lc = NO;
		clearerr((it)->in);
	    }
	    return(chr);
	}else{
	    return(EOF);
	}
    }
}

ungetc_window(chr, it)
    register IO_BACKET	*it;
    register int  chr;
{
    if(chr == EOF) return;
    if(use_windows){
	if(chr == '\n') it->buf_lc++;
	it->buf_cc++;
	if(it->buf_p2 == &(it->buffer[0]))
	    it->buf_p2 = &(it->buffer[IO_BUFSIZ]);
	*--(it->buf_p2) = chr;
    }else{
	it->buf_cc = chr;
    }
}

int request_keyboard(it)
    register IO_BACKET	*it;
{
    register int mask;
    if(use_windows){
	fflush(stdout);
	mask = sigblock(sigmask(SIGINT));
	if(it->buf_lc == 0){
	    it->kb_req++;
	    sigsetmask(mask);
	    return(NO);
	}else{
	    sigsetmask(mask);
	    return(YES);
	}
    }else{
	return(YES);
    }
}

request_console()
{
    if(use_windows){
	fflush(stdout);
	io_table[0].kb_req++;
	while(io_table[0].kb_req > 0) pause();
    }
}

static keyboard_to_buffer(it)
    register IO_BACKET	*it;
{
    register int  chr;

    do{
	chr = getchar();
	if(it->buf_cc < IO_BUFSIZ-64 || chr == '\n'){
	    *(it->buf_p1)++ = chr;
	    if(it->buf_p1 >= &(it->buffer[IO_BUFSIZ]))
		it->buf_p1 = &(it->buffer[0]);
	    it->buf_cc++;
	}
    } while(chr != '\n');
    it->buf_lc++;
}

static keyboard_eof_to_buffer(it)
    register IO_BACKET	*it;
{
    *(it->buf_p1)++ = EOF;
    if(it->buf_p1 >= &(it->buffer[IO_BUFSIZ]))
	it->buf_p1 = &(it->buffer[0]);
    it->buf_cc++;
    it->buf_lc++;
}


/*************************************************************************
*   Keyboard Interrupt.							 *
*************************************************************************/

static keyboard_interrupt()
{
    register IO_BACKET	*it;
    register int  chr, x;

    chr = getchar();
    if(chr > 'A' && chr < 'A'+MAX_OF_WINDOW){		/** Input to Window **/
	it = &io_table[chr-'A'];
	if(it->status&IO_ACTIVE){
	    keyboard_to_buffer(it);
	    if(it->kb_req > 0){
		it->kb_req--;
		it->inp_flag = YES;
		SetKeyboardFlag();
	    }
	    return;
	}
    }else if(chr == 'A'){			       /** Input to Console **/
	if(io_table[0].kb_req > 0){
	    io_table[0].kb_req--;
	    return;
	}
    }else if(chr > 'a' && chr < 'a'+MAX_OF_WINDOW){ /** Interrupt to Window **/
	it = &io_table[chr-'a'];
	if(it->status&IO_ACTIVE){
	    x = 0;
	    while((chr = getchar()) != '\n') x = x*10+chr-'0';
	    if(x==9){  /* EOF */
		keyboard_eof_to_buffer(it);
		if(it->kb_req > 0){
		    it->kb_req--;
		    it->inp_flag = YES;
		    SetKeyboardFlag();
		}
	    }else{
		it->int_code = x;
		SetKeyIntFlag();
	    }
	    return;
	}
    }else if(chr == '?'){
	trace_interrupt();
    }else if(chr == '!'){
	SetHeapGcFlag();
    }else if(chr == '\n'){
	return;
    }
    while(getchar() != '\n');
}

do_keyboard_interrupt()
{
    register IO_BACKET *it;
    register CELL *c, *v;
    register int n;
    CELL hook, list;

    current_predicate = NULL;
    for(n = MAX_OF_WINDOW, it = &io_table[1]; --n; it++){
	if(it->status&IO_ACTIVE){
	    if(it->inp_flag){
		hook = *(it->inp_hook);
		AllocCons(c);
		AllocUndef(v);
		SetAll(&list, LIST, c, MRBOFF);
		SetAll(&c[0], ATOM, NIL, MRBOFF);  /* !? */
		SetAll(&c[1], REF, v, MRBOFF);
		SetAll(it->inp_hook, REF, v, MRBOFF);
		active_unify_with_list(&hook, &list);
		it->inp_flag = NO;
	    }
	    if(it->int_code > 0){
		hook = *(it->int_hook);
		AllocCons(c);
		AllocUndef(v);
		SetAll(&list, LIST, c, MRBOFF);
		SetAll(&c[0], INT, it->int_code, MRBOFF);
		SetAll(&c[1], REF, v, MRBOFF);
		SetAll(it->int_hook, REF, v, MRBOFF);
		active_unify_with_list(&hook, &list);
		it->int_code = 0;
	    }
	}
    }
}

static keyboard_interrupt_without_emacs()
{
    CHAR  buf[10];
    for(;;){
	if(read_console("\nPDSS-KL1 Interruption (? for help)% ", buf, 10) < 0)
	    exit_pdss(1);
	switch(buf[0]){
	  case '?':
	    printf("    c - continue.\n");
	    printf("    g - request gc.\n");
	    printf("    t - start tracing.\n");
	    printf("    s - statistics.\n");
	    printf("    a - abort task.\n");
	    printf("    e - exit emulator.\n");
	    printf("    ?   help.\n");
	    continue;
	  case 'c':
	    return;
	  case 'g':
	    SetHeapGcFlag();
	    return;
	  case 't':
	    trace_interrupt();
	    return;
	  case 's':
	    if(io_table[1].status&IO_ACTIVE){
		io_table[1].int_code = 2;
		SetKeyIntFlag();
	    }
	    return;
	  case 'a':
	    if(io_table[1].status&IO_ACTIVE){
		io_table[1].int_code = 1;
		SetKeyIntFlag();
	    }
	    return;
	  case 'e':
	    exit_pdss(0);
	}
    }
}


/*************************************************************************
*   Check Goal is Hooked.						 *
*************************************************************************/

int is_there_goal_waiting_for_keyboard_input()
{
    IO_BACKET	  *it;
    register CELL *c;
    register int  i;

    it = &io_table[1];
    for(i=1; i<MAX_OF_WINDOW; i++,it++){
	if(it->status&IO_ACTIVE){
	    c = it->inp_hook;
	  loop:
	    while(Typeof(c) == REF) c = Objectof(c);
	    if(Typeof(c) == HOOK || Typeof(c) == MHOOK) return(YES);
	    if(Typeof(c) == MGHOK){
		c = MergerTailof(c);
		goto loop;
	    }
	}
    }
    return(NO);
}

int is_there_goal_waiting_for_keyboard_interrupt()
{
    IO_BACKET	  *it;
    register CELL *c;
    register int  i;

    it = &io_table[1];
    for(i=1; i<MAX_OF_WINDOW; i++,it++){
	if(it->status&IO_ACTIVE){
	    c = it->int_hook;
	  loop:
	    while(Typeof(c) == REF) c = Objectof(c);
	    if(Typeof(c) == HOOK || Typeof(c) == MHOOK) return(YES);
	    if(Typeof(c) == MGHOK){
		c = MergerTailof(c);
		goto loop;
	    }
	}
    }
    return(NO);
}
