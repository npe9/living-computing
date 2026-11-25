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
#include "instr.h"

main(argc, argv_)
    int	 argc;
    char **argv_;
{
    CHAR **argv = (CHAR **)argv_;  /* PORT */
    CHAR file_name[256];
    int	 i, len;
    OBJ	 *module_top;
    MODULE_ENTRY *mod_table;
    FILE *fp;

    initialize_instruction_table();
    initialize_atom_table();
    initialize_code(500000);
    printf("**** PDSS-INVASM %s (%s) ****\n", version, makedate);
    for(i=1; i<argc; i++){
	len = strlen(argv[i]);
	if(strcmp(&argv[i][len-4], ".sav") == 0)
	    argv[i][len-4] = 0;
	AdjustPC(C);
	module_top = C;
	sprintf(file_name, "%s.sav", argv[i]);
	if((fp = fopen(file_name, "r")) == NULL){
	    printf("\nCan't open file \"%s\"\n", file_name);
	    exit_pdss(1);
	}
	if(load_module(fp, &mod_table)){
	    printf("\nCan't inverse assemble file \"%s\"\n", file_name);
	    fclose(fp);
	    exit_pdss(1);
	}
	invasm_module(module_top);
    }
    fclose(fp);
    exit_pdss(0);
}


OBJ *invasm_predicate();

invasm_module(cp)
    OBJ	 *cp;
{
    OBJ	 *module_bottom, *program_bottom, *top;
    unsigned int table_num, code_size, i;
    int	 cnst_offs;

    top = cp;
    printf("000000: module          %s\n", atom_name(GetModuleName(cp)));
    code_size = GetModPredSize(cp+MODULE_CODE_SIZE);
    table_num = GetUShort(cp+MODULE_NUMBER_OF_ENTRY);
    cnst_offs = GetRelAddr(cp+MODULE_CONSTANT_OFFSET);
    module_bottom = cp+code_size+MODULE_SIZE_LENGTH;
    if(cnst_offs == 0){
	program_bottom = module_bottom;
    }else{
	program_bottom = cp+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    cp += MODULE_HEADER_LENGTH;
    cp += ENTRY_TABLE_HASH_TABLE_SIZE;

    for(i=0; i<table_num; i++){	 /** Public Predicate Entry Table **/
	printf("        public          %s/%d\n",
	       atom_name(GetPredID(cp+PRED_of_ENTRY_TABLE)&0xFFFF),
	       (GetPredID(cp+PRED_of_ENTRY_TABLE)>>16));
	cp += ELEN_of_ENTRY_TABLE;
    }
    while(cp+PREDICATE_HEADER_LENGTH < program_bottom){
	cp = invasm_predicate(cp, top);
    }
    AdjustPC(cp);
    if(cp < module_bottom) invasm_constant(cp, module_bottom, top);
}

OBJ *invasm_predicate(cp, top)
    OBJ	 *cp, *top;
{
    OBJ	 *op_bottom;
    unsigned int code_size, pre_name, op_code, size, mask, i;
    int	 special;
    CHAR string_buffer[255];

    code_size = GetModPredSize(cp+PREDICATE_CODE_SIZE);
    pre_name = GetAtom(cp+PREDICATE_NAME);
    op_bottom = cp+code_size+PREDICATE_SIZE_LENGTH;
    printf("        predicate       %s/%d\n", 
	   atom_name(pre_name),
	   GetPredArity(cp+PREDICATE_ARITY));
    cp += PREDICATE_HEADER_LENGTH;

    while(cp < op_bottom){
	inverse_assemble_one(cp, top, &string_buffer[0]);
	printf("%s\n", string_buffer);
	op_code = GetOpCode(cp);
	special = NO;
	if(op_code == SPECIAL_FUNCTION_SHIFT){
	    cp++;
	    op_code = 0x100|GetOpCode(cp);
	    special = YES;
	}
	switch(instruction_table[op_code].type){
	  case NO_ARG: cp += special ? LEN_of_2B_NO_ARG : LEN_of_NO_ARG; break;
	  case REG:    cp += special ? LEN_of_2B_REG	: LEN_of_REG;	 break;
	  case REGS2:  cp += special ? LEN_of_2B_REGS2	: LEN_of_REGS2;	 break;
	  case REGS3:  cp += special ? LEN_of_2B_REGS3	: LEN_of_REGS3;	 break;
	  case REGS4:  cp += special ? LEN_of_2B_REGS4	: LEN_of_REGS4;	 break;
	  case REGS5:  cp += special ? LEN_of_2B_REGS5	: LEN_of_REGS5;	 break;
	  case REGS6:  cp += special ? LEN_of_2B_REGS6	: LEN_of_REGS6;	 break;
	  case REGS7:  cp += special ? LEN_of_2B_REGS7	: LEN_of_REGS7;	 break;
	  case REGS8:  cp += special ? LEN_of_2B_REGS8	: LEN_of_REGS8;	 break;

	  case REG_ATM:		cp += LEN_of_REG_ATM;	    break;
	  case REG_ATM_LAB:	cp += LEN_of_REG_ATM_LAB;   break;
	  case REG_IT:		cp += LEN_of_REG_IT;	    break;
	  case REG_IT_LAB:	cp += LEN_of_REG_IT_LAB;    break;
	  case REG_FLOT:	cp += LEN_of_REG_FLOT;	    break;
	  case REG_FLOT_LAB:	cp += LEN_of_REG_FLOT_LAB;  break;
	  case REG_ARITY:	cp += LEN_of_REG_ARITY;	    break;
	  case REG_ARITY_LAB:	cp += LEN_of_REG_ARITY_LAB; break;
	  case REG_LAB:		cp += LEN_of_REG_LAB;	    break;
	  case REG_LAB6:	cp += LEN_of_REG_LAB6;	    break;

	  case REG_IDX:		cp += LEN_of_REG_IDX;	   break;
	  case REG_IDX_REG:	cp += LEN_of_REG_IDX_REG;  break;
	  case REG_IDX_ATM:	cp += LEN_of_REG_IDX_ATM;  break;
	  case REG_IDX_IT:	cp += LEN_of_REG_IDX_IT;   break;
	  case REG_IDX_FLOT:	cp += LEN_of_REG_IDX_FLOT; break;

	  case ARG:		cp += LEN_of_ARG;      break;
	  case ARG_REG:		cp += LEN_of_ARG_REG;  break;
	  case ARG_ATM:		cp += LEN_of_ARG_ATM;  break;
	  case ARG_IT:		cp += LEN_of_ARG_IT;   break;
	  case ARG_FLOT:	cp += LEN_of_ARG_FLOT; break;
	  case ARG_LAB:		cp += LEN_of_ARG_LAB;  break;

	  case LAB:		cp += LEN_of_LAB;	      break;
	  case PARITY:		cp += LEN_of_PARITY;	      break;
	  case PARITY_LAB:	cp += LEN_of_PARITY_LAB;      break;
	  case PARITY_LAB_REG:	cp += LEN_of_PARITY_LAB_REG;  break;
	  case MOD_PRED_PARITY: cp += LEN_of_MOD_PRED_PARITY; break;

	  case REG_REG_ATM:	cp += LEN_of_REG_REG_ATM;     break;
	  case REG_ARITY_ATM:	cp += LEN_of_REG_ARITY_ATM;   break;
	  case REG_LAB_REG_REG: cp += LEN_of_REG_LAB_REG_REG; break;
	  case REG_REG_REP:	cp += LEN_of_REG_REG_REP;     break;
	  case ARG_REG_REP:	cp += LEN_of_ARG_REG_REP;     break;
	  case REG_IDX_REG_REP:	cp += LEN_of_REG_IDX_REG_REP; break;

	  case JUMP_ON:		
	    size = GetUShort(cp+SIZE_of_JUMP_ON);
	    cp += TABLE_of_JUMP_ON;
	    while(size--){
		printf("        table_entry     %06x\n",
		       GetAddr(cp+LAB_of_JUMP_ON)-top);
		cp += ELEN_of_JUMP_ON;
	    }
	    AdjustPCunlessPackedCode(cp);
	    break;
	  case BRANCH_ON_I:
	    size = GetUShort(cp+SIZE_of_BRANCH_ON_I);
	    cp += TABLE_of_BRANCH_ON_I;
	    while(size--){
		printf("        bucket_entry    %d, %06x\n",
		       GetInt(cp+IT_of_BRANCH_ON_I),
		       GetAddr(cp+LAB_of_BRANCH_ON_I)-top);
		cp += ELEN_of_BRANCH_ON_I;
	    }
	    break;
	  case BRANCH_ON_A:
	    size = GetUShort(cp+SIZE_of_BRANCH_ON_A);
	    cp += TABLE_of_BRANCH_ON_A;
	    while(size--){
		printf("        bucket_entry    %s, %06x\n",
		       atom_name(GetAtom(cp+ATM_of_BRANCH_ON_A)),
		       GetAddr(cp+LAB_of_BRANCH_ON_I)-top);
		cp += ELEN_of_BRANCH_ON_A;
	    }
	    break;
	  case HASH_ON_I:
	    mask = GetUShort(cp+MASK_of_HASH_ON_I);
	    cp += TABLE_of_HASH_ON_I;
	    for(i=size=0; i<=mask; i++){
		size += GetUShort(cp+CNUM_of_HASH_ON_I);
		cp += TLEN_of_HASH_ON_I;
	    }
	    while(size--){
		printf("        bucket_entry    %d, %06x\n",
		       GetInt(cp+IT_of_HASH_ON_I),
		       GetAddr(cp+LAB_of_HASH_ON_I)-top);
		cp += ELEN_of_HASH_ON_I;
	    }
	    break;
	  case HASH_ON_A:
	    mask = GetUShort(cp+MASK_of_HASH_ON_A);
	    cp += TABLE_of_HASH_ON_A;
	    for(i=size=0; i<=mask; i++){
		size += GetUShort(cp+CNUM_of_HASH_ON_A);
		cp += TLEN_of_HASH_ON_A;
	    }
	    while(size--){
		printf("        bucket_entry    %s, %06x\n",
		       atom_name(GetAtom(cp+ATM_of_HASH_ON_A)),
		       GetAddr(cp+LAB_of_HASH_ON_I)-top);
		cp += ELEN_of_HASH_ON_A;
	    }
	    break;
	  default:
	    return(op_bottom);
	}
    }
    return(op_bottom);
}

invasm_constant(p, bottom, top)
    CELL *p, *bottom, *top;
{
    int fw;
    while(p < bottom){
	switch(Typeof(p)){
	  case ATOM:
	    printf("%06x: define_atom     %s\n",
		   (int)p-(int)top, atom_name(Valueof(p)));
	    break;
	  case INT:
	    printf("%06x: define_int      %d\n", (int)p-(int)top, Valueof(p));
	    break;
	  case FLOAT:
	    fw = Valueof(p);
	    printf("%06x: define_int      %s\n", (int)p-(int)top,
		   float_to_string(&fw));
	    break;
	  case DESC:
	    printf("%06x: define_desc     %02x, %d\n", (int)p-(int)top,
		   (Valueof(p)>>24)&0xFF, Valueof(p)&0xFFFFFF);
	    break;
	  case LIST:
	    printf("%06x: define_list     %06x\n",
		   (int)p-(int)top, Valueof(p)-(int)top);
	    break;
	  case VECTOR:
	    printf("%06x: define_vect     %06x\n",
		   (int)p-(int)top, Valueof(p)-(int)top);
	    break;
	  case STRING:
	    printf("%06x: define_string   %06x\n",
		   (int)p-(int)top, Valueof(p)-(int)top);
	    break;
	  case 0xFF:
	    printf("%06x: begin_const_section  %06x\n",
		   (int)p-(int)top, Valueof(p)-(int)top);
	    break;
	}
	p++;
    }
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
assemble()			   { exit_pdss(1); }
CHAR *expand_path_name()	   { exit_pdss(1); }
