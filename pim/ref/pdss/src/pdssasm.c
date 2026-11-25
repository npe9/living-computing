/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "klb.h"

main(argc, argv)
    int	 argc;
    CHAR **argv;
{
    CHAR file_name[256];
    FILE *fp;
    int	 i, len;
    MODULE_ENTRY *mod_table;
    OBJ  *C0;

    initialize_instruction_table();
    initialize_atom_table();
    initialize_code(500000);
    AdjustPC(C);
    printf("**** PDSS-ASM %s (%s) ****\n", version, makedate);
    for(i=1,C0=C; i<argc; i++,C=C0){
	len = strlen(argv[i]);
	if(strcmp(&argv[i][len-4], ".asm") == 0)
	    argv[i][len-4] = 0;
	printf("Make save file %s...", argv[i]);
	fflush(stdout);
	sprintf(file_name, "%s.asm", argv[i]);
	if((fp = fopen(file_name, "r")) == NULL){
	    printf("\nCan't open file \"%s\"\n", file_name);
	    exit_pdss(1);
	}
	if(assemble(fp, &mod_table)){
	    printf("\nCan't assemble file \"%s\"\n", file_name);
	    fclose(fp);
	    exit_pdss(1);
	}
	fclose(fp);
	sprintf(file_name, "%s.sav", argv[i]);
	if((fp = fopen(file_name, "w")) == NULL){
	    printf("\nCan't write file \"%s\"\n", file_name);
	    exit_pdss(1);
	}
	save_module(fp, mod_table);
	printf(" OK\n");
    }
    exit_pdss(0);
}

exit_pdss(code)
    int code;
{
    exit(code);
}

/** Dunny **/
int use_windows = NO;
int current_window;
int gc_counter;
int gc_panic_flag;
int iflag;
dcode_function_to_mod_pred_arity() { exit_pdss(1); }
load_and_link_native_code_module() { exit_pdss(1); }
CHAR *expand_path_name()	   { exit_pdss(1); }
