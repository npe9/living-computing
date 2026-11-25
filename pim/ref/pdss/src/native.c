/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#if 0 /* PORT: no a.out native-code loading; was #ifndef mips */

#include <a.out.h>
#include <sys/file.h>
#include "pdss.h"
#include "memory.h"
#include "io.h"

int load_and_link_native_code_module(fname, mod_table)
    CHAR *fname;
    MODULE_ENTRY **mod_table;
{
    struct exec header;
    int	 file;
    int	 (*initialize)();
    int	 readsize;
    OBJ	 *addr;
    unsigned int module;
    PREDICATE_ENTRY *pt, **pft, **fpt;
    CHAR name[512];
    char command[320], tmp[24];

    PrintCons("\nLoad Native Code.."); Flush();
    if(expand_path_name(fname, name) == NULL){
	PrintCons(" Fail.\n"); Flush();
	return(NLOAD_CANNOT_OPEN_FILE);
    }
    if((file = open(name, O_RDONLY)) < 0){
	PrintCons(" Fail.\n"); Flush();
	return(NLOAD_CANNOT_OPEN_FILE);
    }
    close(file);

    PrintCons(" Link"); Flush();
    sprintf(tmp, "/tmp/pdss%d.nc", getpid());  /* Temporary file */
    sprintf(command, "ld -r -s -A %s -T %x %s -e _initialize_module -o %s",
	    PDSS_OBJECT_FILE, sbrk(0), name, tmp);
    if(system(command) != 0){
	PrintCons(" Fail.\n"); Flush();
	unlink(tmp);
	return(NLOAD_LINK_ERROR);
    }

    PrintCons("/Load"); Flush();
    if((file = open(tmp, O_RDONLY)) < 0){
	PrintCons(" Fail.\n"); Flush();
	unlink(tmp);
	return(NLOAD_CANNOT_OPEN_FILE);
    }
    read(file, &header, sizeof(struct exec));
    readsize = header.a_text+header.a_data;
    if((int)(addr = (OBJ *)sbrk(readsize+header.a_bss)) == -1){
	PrintCons(" Can't Get Memory.\n"); Flush();
	close(file); unlink(tmp);
	return(NLOAD_MEMORY_LIMIT);
    }
    bzero(addr+readsize, header.a_bss);
    read(file, addr, readsize);
    close(file); unlink(tmp);

    initialize = (int (*) ())header.a_entry;
    PrintCons2F("/Init(%x,%x)", initialize, readsize+header.a_bss); Flush();
    module = initialize(&pt, &pft, &fpt);
    if(!enter_module(module, addr, readsize+header.a_bss, mod_table)){
	PrintCons(" Fail.\n"); Flush();
	return(NLOAD_MODULE_PROTECTED);
    }
    (*mod_table)->predicate_tbl = pt;
    (*mod_table)->pid_func_hash_tbl = pft;
    (*mod_table)->func_pid_hash_tbl = fpt;
    PrintCons("/Done.\n"); Flush();
    return(NLOAD_SUCCESS);
}

#else

int load_and_link_native_code_module(){};

#endif
