/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include  <stdio.h>
#include  "pdss.h"
/* PORT: forward declarations */
static int read_option_sub();


unsigned int option_heap_size	      = HEAP_SIZE;
unsigned int option_code_size	      = CODE_SIZE;
int	     option_startup_flag      = 1;
CHAR	     option_startup_file[256];
int	     option_load_prompting    = NO;
int	     option_print_var_mode    = 0;
int	     option_use_windows	      = NO;
int	     option_alarm_clock_sw    = YES;
#if TWO_WAY_READY_GOAL_POOL
int	     option_breadth_first     = NO;
unsigned int option_execute_limit     = 0;
int	     option_random_enqueue    = NO;
unsigned int option_random_rate;
unsigned int option_random_seed;
#endif
#if INSTRUCTION_TRACE
int	     option_instruction_trace = NO;
#endif
#if INSTRUCTION_COUNT
int	     option_instruction_count = NO;
#endif

read_option(argc, argv)
    int	 argc;
    CHAR **argv;
{
    CHAR *env, *getenv();
    int	 i;

    sprintf(option_startup_file, "%s/%s", PDSS_SUPDIR, "STARTUP");
    if((env = getenv("PDSSOPT")) != NULL){
	read_option_sub(env);
    }
    for(i = 1; i < argc; i++){
	read_option_sub(argv[i]);
    }
}

static read_option_sub(s)
    CHAR *s;
{
    CHAR f;
    int	 x;

    for(;;){
	while(*s <= ' ') if(*s++ == 0) return;	/* Skip Space */
	if(*s == '-' || *s == '+'){
	    f = *s++;
	    while(*s > ' '){
		switch(*s++){
		  case 'H': case 'h':  /***** Heap Area Size (unit:cell) *****/
		    x = 0;
		    while(*s >= '0' && *s <= '9') x = x*10+(*s++)-'0';
		    option_heap_size = x;
		    break;
		  case 'C': case 'c':  /***** Code Area Size (unit:byte) *****/
		    x = 0;
		    while(*s >= '0' && *s <= '9') x = x*10+(*s++)-'0';
		    option_code_size = x;
		    break;
		  case 'T': case 't':	   /***** Read Startup File Flag *****/
		    option_startup_flag = (f == '+') ? 1 : 0;
		    option_load_prompting = (f != '+');
		    break;
		  case 'L': case 'l':	 /***** Load File Prompting Flag *****/
		    option_load_prompting = YES;
		    break;
		  case 'V': case 'v':	      /***** Print Variable Mode *****/
		    option_print_var_mode = 1;
		    break;
		  case '2':		 /***** Use Windows in GNU Emacs *****/
		    option_use_windows = YES;
		    break;
		  case 'A': case 'a':	 /***** Alarm Clock Interrupt SW *****/
		    option_alarm_clock_sw = NO;
		    break;
#if TWO_WAY_READY_GOAL_POOL
		  case 'B': case 'b':	       /***** Breadth First Flag *****/
		    option_breadth_first = YES;
		    option_random_enqueue = NO;
		    x = 0;
		    while(*s >= '0' && *s <= '9') x = x*10+(*s++)-'0';
		    if(x <= 0) x=100;
		    option_execute_limit = x;
		    break;
		  case 'D': case 'd':	       /***** Depth First Flag *****/
		    option_breadth_first = NO;
		    option_random_enqueue = NO;
		    x = 0;
		    while(*s >= '0' && *s <= '9') x = x*10+(*s++)-'0';
		    if(x <= 0) x=0;
		    option_execute_limit = x;
		    break;
		  case 'R': case 'r':	       /***** Random Enqueue *****/
		    option_random_enqueue = YES;
		    option_random_rate = 5;
		    option_random_seed = 0;
		    option_execute_limit = 0;
		    if(*s >= '0' && *s <= '9'){
			x = 0;
			while(*s >= '0' && *s <= '9') x = x*10+(*s++)-'0';
			if(x < 0) x=0;
			if(x > 100) x=100;
			option_random_rate = x;
		    }
		    if(*s != ',') break;
		    s++;
		    if(*s >= '0' && *s <= '9'){
			x = 0;
			while(*s >= '0' && *s <= '9') x = x*10+(*s++)-'0';
			option_random_seed = x;
		    }
		    if(*s != ',') break;
		    s++;
		    if(*s >= '0' && *s <= '9'){
			x = 0;
			while(*s >= '0' && *s <= '9') x = x*10+(*s++)-'0';
			if(x < 0) x=0;
			option_execute_limit = x;
		    }
		    break;
#endif
#if INSTRUCTION_TRACE
		  case 'I': case 'i':	   /***** Instruction Trace Flag *****/
		    option_instruction_trace = YES;
		    break;
#endif
#if INSTRUCTION_COUNT
		  case '?':		   /***** Instruction Count Flag *****/
		    option_instruction_count = YES;
		    break;
#endif
		  default:
		    fprintf(stderr, "pdss: unknown option \"%c\"\n", s[-1]);
		    exit(1);
		}
	    }
	}else{
	    x = 0;
	    while(*s > ' ') option_startup_file[x++] = *s++;
	    option_startup_file[x] = 0;
	    option_startup_flag = 2;
	}
    }
}
