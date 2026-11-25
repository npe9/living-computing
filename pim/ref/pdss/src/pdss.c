/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#define	 MAIN
#include <sys/time.h>
#include <sys/resource.h>
#include <signal.h>
#include "pdss.h"
#include "io.h"
#include "instr.h"
#include "ctype.h"
/* PORT: forward declarations */
static int load_kl1b_file();
static int load_kl1b_file_and_enter_module();
static OBJ *read_top_level_goal();
static CHAR *scan_name();
static int write_result();


#ifndef sigmask
#define sigmask(m) (1 << ((m)-1))
#endif

static CHAR execute_goal[128];	/** top level goal name **/


/*************************************************************************
*    PDSS Main.								 *
*************************************************************************/

main(argc, argv_)
    int argc; 
    char **argv_;
{
    CHAR **argv = (CHAR **)argv_;  /* PORT */
    OBJ	 *top_level, *read_top_level_goal();
    CHAR yn[2], motd[256];
    FILE *fp;
    int c;

    read_option(argc, argv);
    initialize_io();
    PrintCons2F("***** PDSS-KL1 %s (%s) *****\n", version, makedate);
    sprintf(motd, "%s/MESSAGE", PDSS_LIBDIR);
    if(fp = fopen(motd, "r")){
	while((c = getc(fp)) != EOF) putchar(c);
    }
    initialize_instruction_table();
    initialize_atom_table();
    initialize_float_calculator();
    initialize_exception_tag_table();
    initialize_code(option_code_size);
    initialize_dcode_table();
    load_kl1b_file();
    initialize_code2();
    for(;;){
	initialize_heap(option_heap_size);
	initialize_priority_queue();
	if((top_level = read_top_level_goal()) != NULL){
	    initialize_timer();
	    initialize_shoen_tree(top_level);
	    initialize_tracer();
#ifdef STATISTICS_START
	    STATISTICS_START;
#endif
	    timeit(emulate);
#ifdef STATISTICS_END
	    STATISTICS_END;
#endif
	    write_result();
	}
	for(;;){
	    if(read_console("\nNext Goal ?: ", yn, 2) < 0) exit_pdss(1);
	    if((yn[0] == 'Y') || (yn[0] == 'y')) break;
	    if((yn[0] == 'N') || (yn[0] == 'n') || (yn[0] == 0)) exit_pdss(0);
	}
    }
}

stop_pdss()
{
    io_ctrl_when_stop();
    signal(SIGTSTP, SIG_DFL);
    sigsetmask(sigblock(0) & ~sigmask(SIGTSTP));
    kill(getpid(), SIGTSTP);
    sigblock(sigmask(SIGTSTP));	 /** Stop here **/
    signal(SIGTSTP, SIG_IGN);
    io_ctrl_when_resume();
}

abort_pdss(sig)
    int sig;
{
    exit_pdss((sig == 0) ? 0 : 1);
}

exit_pdss(code)
    int code;
{
    putchar('\n');
    io_ctrl_when_exit();
    exit(code);
}


/*************************************************************************
*    Load KL1-B file.							 *
*************************************************************************/

static load_kl1b_file()
{
    FILE *fp, *fopen();
    CHAR file_name[256];
    int len;

    if(option_startup_flag){
	if((expand_path_name(option_startup_file, file_name) == NULL)
	 ||((fp = fopen(file_name, "r")) == NULL)){
	    if(*option_startup_file == '/' || *option_startup_file == '~')
		goto cannot_open;
	    sprintf(file_name, "%s/%s", PDSS_SUPDIR, option_startup_file);
	    fp = fopen(file_name, "r");
	    if(fp == NULL){
	      cannot_open:
		Error1F("Can't open startup file %s", file_name);
		option_startup_flag = 0;
	    }
	}
    }
    if(option_startup_flag){
	for(;;){
	    if(fgets(file_name, 128, fp) == NULL) goto no_execute_goal;
	    len = strlen(file_name);
	    if(len < 2) break;
	    file_name[len-1] = 0;  /* remove LF */
	    load_kl1b_file_and_enter_module(file_name);
	}
	PrintCons("\n");
	if(fgets(execute_goal, 128, fp)){
	    len = strlen(execute_goal);
	    if(len < 2) goto no_execute_goal;
	    execute_goal[len-1] = 0;  /* remove LF */
	}else{
	  no_execute_goal:
	    option_startup_flag = 0;
	}
	fclose(fp);
    }
    if(option_load_prompting){
	MODULE_ENTRY *mod_table;
	for(;;){
	    PrintCons("\n");
	    if(read_console("Code file name : ", file_name, 128) < 0)
		exit_pdss(1);
	    if(file_name[0] == 0) return;
	    if(load_from_sav_or_asm_file(file_name, &mod_table)){
		Error1F("\nCannot Load File: %s", file_name);
	    }
	}
    }
}

static load_kl1b_file_and_enter_module(file)
    CHAR *file;
{
    int protect;
    MODULE_ENTRY *mod_table;
    CHAR buf[256];
    if(*file == '!'){
	file++;
	protect = YES;
    }else{
	protect = NO;
    }
    while(*file == ' ') file++;
    if(*file != '/'){
	sprintf(buf, "%s/%s", PDSS_LIBDIR, file);
	file = buf;
    }
    if(option_startup_flag == 2){
	PrintCons1F("Loading... %s ....", file); Flush();
    }else{
	PrintCons("."); Flush();
    }
    if(load_from_sav_or_asm_file(file, &mod_table)){
	Error1F("\nRuntime Code Loading Error: %s", file);
	exit_pdss(1);
    }
    if(protect) mod_table->protect = YES;
    if(option_startup_flag == 2) PrintCons("OK.\n");
}


/*************************************************************************
*    Read Top Level Goal.						 *
*************************************************************************/

static OBJ *read_top_level_goal()
{
    CHAR *module, *predicate, *c, *scan_name();
    int	 mid, pid;
    MODULE_ENTRY *addr;
    OBJ *code;

    for(;;){
	if(!option_startup_flag){
	    if(read_console("goal>> ", execute_goal, 128) < 0) exit_pdss(1);
	    if(execute_goal[0] == 0) return(NULL);
	}
	c = execute_goal;
	module = scan_name(&c);
	if(module == NULL || *c != ':'){
	    goto bad_pred_name;
	}
	*c++ = 0;
	predicate = scan_name(&c);
	if(predicate == NULL || (*c != '.' && *c != 0)){
      bad_pred_name:
	    Error1F("Illegal predicate name: %s.", execute_goal);
	    option_startup_flag = 0;
	    continue;
	}
	*c = 0;
	mid = intern_atom(module);
	if(lookup_module(mid, &addr) == MODMAN_MODULE_NOT_FOUND){
	    Error1F("Undefined module: %s.", module);
	    option_startup_flag = 0;
	    continue;
	}
	pid = intern_atom(predicate);	/* arity == 0 */
	code = find_predicate(addr, pid);
	if(code == NULL){
	    Error2F("Undefined predicate: %s:%s.", module, predicate);
	    option_startup_flag = 0;
	    continue;
	}
	if(option_startup_flag){
	    option_startup_flag = 0;
	}else{
	    set_module_trace_flag(mid, YES);
	}
	return(code);
    }
}

static CHAR *scan_name(s)
    CHAR **s;
{
    register CHAR *p = *s, *q;
    while(IsBlank(*p)) p++;
    q = p;
    if(*p == '\''){		/* quoted atom */
	CHAR *qq;
	q = qq = ++p;		/* skip quote */
	while(*p != '\''){
      quote2:
	    *qq++ = *p;
	    if(*p++ == 0) return(NULL); /* non-terminating atom */
	}
	if(*++p == '\'') goto quote2;	/** " '' " ==> " ' " **/
	*qq++ = 0;
    }else if(*p=='['){		/* '[]' ? */
	if(*++p != ']') return(NULL);
	p++;
    }else if(IsAlpha(*p)){
	while(IsAlNum(*++p));
    }else if(IsSymbol(*p)){
	while(IsSymbol(*++p));
    }else if(IsSpcial(*p)){
	while(IsSpcial(*++p));
    }else{
	return(NULL);
    }
    if(IsBlank(*p)){
	*p++ = 0;
	while(IsBlank(*p)) p++;
    }
    *s = p;
    return(q);
}


/*************************************************************************
*    Write Result.							 *
*************************************************************************/

static write_result()
{
    int reductions;
    CELL *tmp;
    Dereference2(result_of_grand_mother, tmp);
    reductions = grand_mother->total_of_reduction;
    if(Typeof(tmp) ==  LIST){
	SelectWindow(CONSOLE);
	print_term(tmp, PRINT_LENGTH, PRINT_DEPTH);
	PrintCons1F("\n%12d reductions.\n", reductions);
#if INSTRUCTION_COUNT
	PrintCons1F("%12d instructions.\n\n", instruction_counter);
	if(option_instruction_count) print_instr_counter();
#endif
	return;
    }else{
	PrintCons("\nDeadlock or Error ?\n");
#if INSTRUCTION_COUNT
	PrintCons1F("%12d instructions.\n\n", instruction_counter);
	if(option_instruction_count) print_instr_counter();
#endif
    }
}

#if INSTRUCTION_COUNT
print_instr_counter()
{
    register struct instr_rec *op;
    register int i;
    SelectWindow(CONSOLE);
    for(i=0; i<256; i++){
	op = &instruction_table[i];
	if(op->mnem != NULL){
#if INSTRUCTION_BRANCH_COUNT
	    if(instr__branch_acp[i] || instr__branch_lab[i]){
		printf("%10u %10u %10u  %s\n", instr__counter[i],
		       instr__branch_acp[i], instr__branch_lab[i], op->mnem);
	    }else{
		printf("%10u                        %s\n", instr__counter[i],
		       op->mnem);
	    }
#else
	    printf("%10u  %s\n", instr__counter[i], op->mnem);
#endif
	}
    }
}
#endif


/*************************************************************************
*    Execute Function & Display CPU Time.				 *
*************************************************************************/

timeit(routine)
    int (* routine)();
{
    long uspent, sspent;
    struct rusage usage_before, usage_after;
    getrusage(RUSAGE_SELF, &usage_before);
    routine();
    getrusage(RUSAGE_SELF, &usage_after);
    uspent = (usage_after.ru_utime.tv_sec-usage_before.ru_utime.tv_sec)*1000
	   + (usage_after.ru_utime.tv_usec-usage_before.ru_utime.tv_usec)/1000;
    sspent = (usage_after.ru_stime.tv_sec-usage_before.ru_stime.tv_sec)*1000
	   + (usage_after.ru_stime.tv_usec-usage_before.ru_stime.tv_usec)/1000;
    PrintCons2F("\nSystem: %8d msec\nUser: %10d msec\n", sspent, uspent);
}
