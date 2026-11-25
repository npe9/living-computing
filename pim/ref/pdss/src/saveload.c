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

#define SAV_MAGIC  ZZ(0xA5C3,0xA5C5,0xA5C7,0xA5C9)
#define SAV_VRSON1 0x25
#define SAV_VRSON2 0x25
#define ATOMMAX	   4096
static unsigned short atom_id_table[ATOMMAX];


/*************************************************************************
*   Save Module -- Macros.						 *
*************************************************************************/

#define Write1C(c, fp){\
    putc(c, fp);\
}
#define Write2C(x, fp){\
    int xx = (x);\
    putc(xx>>8, fp);\
    putc(xx, fp);\
}
#define Write4C(x, fp){\
    int xx = (x);\
    putc(xx>>24, fp);\
    putc(xx>>16, fp);\
    putc(xx>>8, fp);\
    putc(xx, fp);\
}

#define WriteOpCode(x, fp)	Write1C(x, fp)
#define WriteReg(x, fp)		Write1C(x, fp)
#define WriteAtom(x, fp)	Write2C(convert_atom_id(x), fp)
#define WriteInt(x, fp)		Write4C(x, fp)
#define WriteFloat(x, fp)	Write4C(x, fp)
#define WriteArity(x, fp)	Write1C(x, fp)
#define WriteIndex(x, fp)	Write1C(x, fp)
#define WriteRepnum(x, fp)	Write1C(x, fp)
#define WritePredArity(x, fp)	Write1C(x, fp)
#define WritePredID(x, fp)	Write4C(x, fp)
#if KLB_4BYTE_REL_ADDR
#define WriteRelAddr(x, fp)	Write4C(x, fp)
#define WriteModPredSize(x, fp) Write4C(x, fp)
#else
#define WriteRelAddr(x, fp)	Write2C(x, fp)
#define WriteModPredSize(x, fp) Write2C(x, fp)
#endif
#define WriteChar(x, fp)	Write1C(x, fp)
#define WriteShort(x, fp)	Write2C(x, fp)
#define WriteLong(x, fp)	Write4C(x, fp)

static OBJ *enter_atoms_in_predicate();
static unsigned int convert_atom_id();
static OBJ *write_predicate();


/*************************************************************************
*   Save Module -- Main.						 *
*************************************************************************/

save_module(file, module)
    FILE *file;
    MODULE_ENTRY *module;
{    
    OBJ *cp = module->addr;
    WriteShort(SAV_MAGIC, file);
    WriteChar(SAV_VRSON1, file);
    WriteChar(SAV_VRSON2, file);
    make_atom_table(cp);
    write_atom_table(file);
    write_code_body(cp, file);
}


/*************************************************************************
*   Save Module -- Make Atom Table.					 *
*************************************************************************/

static make_atom_table(cp)
    OBJ *cp;
{
    OBJ *module_bottom, *program_bottom;
    unsigned int module_name, table_num, code_size, i;
    int cnst_offs;

    /**** Initialize Atom ID Convert Table ****/
    for(i=0; i<ATOMMAX; i++) atom_id_table[i] = 0xFFFF;

    /**** Enter Atoms in Module Header ****/
    code_size = GetModPredSize(cp+MODULE_CODE_SIZE);
    module_name = GetAtom(cp+MODULE_NAME);
    table_num = GetUShort(cp+MODULE_NUMBER_OF_ENTRY);
    cnst_offs = GetRelAddr(cp+MODULE_CONSTANT_OFFSET);
    enter_atom(module_name);
    module_bottom = cp+code_size+MODULE_SIZE_LENGTH;
    if(cnst_offs == 0){
	program_bottom = module_bottom;
    }else{
	program_bottom = cp+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    cp += MODULE_HEADER_LENGTH;

    /**** Enter Atoms in Entry Table ****/
    cp += ENTRY_TABLE_HASH_TABLE_SIZE;
    for(i=0; i<table_num; i++){
	enter_atom(GetPredID(cp+PRED_of_ENTRY_TABLE)&0xFFFF);
	cp += ELEN_of_ENTRY_TABLE;
    }

    /**** Enter Atoms in Predicates ****/
    while(cp+PREDICATE_HEADER_LENGTH < program_bottom){
	cp = enter_atoms_in_predicate(cp);
    }
    AdjustPC(cp);

    /**** Enter Atoms in Structured Constant ****/
    if(cp < module_bottom){
	enter_atoms_in_constant_section(cp, module_bottom);
    }
}

static OBJ *enter_atoms_in_predicate(cp)
    OBJ *cp;
{	  
    OBJ *op_bottom, *base;
    unsigned int code_size, pre_name, op_code, special, size, mask, i;

    /**** Enter Atoms in Predicate Header ****/
    base = cp;
    cp += PREDICATE_HEADER_LENGTH;
    code_size = GetPredicateSize(cp);
    pre_name = GetPredicateName(cp);
    op_bottom = base+code_size+PREDICATE_SIZE_LENGTH;
    enter_atom(pre_name);

    /**** Enter Atoms in Predicate Body ****/
    while(cp <	op_bottom){
	op_code = GetOpCode(cp);
	special = NO;
	if(op_code == SPECIAL_FUNCTION_SHIFT){
	    cp++;
	    op_code = 0x100|GetOpCode(cp);
	    special = YES;
	}
	switch(GetInstrType(op_code)){
	  case NO_ARG: cp += special ? LEN_of_2B_NO_ARG : LEN_of_NO_ARG; break;
	  case REG:    cp += special ? LEN_of_2B_REG	: LEN_of_REG;	 break;
	  case REGS2:  cp += special ? LEN_of_2B_REGS2	: LEN_of_REGS2;	 break;
	  case REGS3:  cp += special ? LEN_of_2B_REGS3	: LEN_of_REGS3;	 break;
	  case REGS4:  cp += special ? LEN_of_2B_REGS4	: LEN_of_REGS4;	 break;
	  case REGS5:  cp += special ? LEN_of_2B_REGS5	: LEN_of_REGS5;	 break;
	  case REGS6:  cp += special ? LEN_of_2B_REGS6	: LEN_of_REGS6;	 break;
	  case REGS7:  cp += special ? LEN_of_2B_REGS7	: LEN_of_REGS7;	 break;
	  case REGS8:  cp += special ? LEN_of_2B_REGS8	: LEN_of_REGS8;	 break;

	  case REG_ATM:		enter_atom(GetAtom(cp+ATM_of_REG_ATM));
				cp += LEN_of_REG_ATM;		break;
	  case REG_ATM_LAB:	enter_atom(GetAtom(cp+ATM_of_REG_ATM_LAB));
				cp += LEN_of_REG_ATM_LAB;	break;
	  case REG_IT:		cp += LEN_of_REG_IT;		break;
	  case REG_IT_LAB:	cp += LEN_of_REG_IT_LAB;	break;
	  case REG_FLOT:	cp += LEN_of_REG_FLOT;		break;
	  case REG_FLOT_LAB:	cp += LEN_of_REG_FLOT_LAB;	break;
	  case REG_ARITY:	cp += LEN_of_REG_ARITY;		break;
	  case REG_ARITY_LAB:	cp += LEN_of_REG_ARITY_LAB;	break;
	  case REG_LAB:		cp += LEN_of_REG_LAB;		break;
	  case REG_LAB6:	cp += LEN_of_REG_LAB6;		break;

	  case REG_IDX:		cp += LEN_of_REG_IDX;		break;
	  case REG_IDX_REG:	cp += LEN_of_REG_IDX_REG;	break;
	  case REG_IDX_ATM:	enter_atom(GetAtom(cp+ATM_of_REG_IDX_ATM));
				cp += LEN_of_REG_IDX_ATM;	break;
	  case REG_IDX_IT:	cp += LEN_of_REG_IDX_IT;	break;
	  case REG_IDX_FLOT:	cp += LEN_of_REG_IDX_FLOT;	break;

	  case ARG:		cp += LEN_of_ARG;		break;
	  case ARG_REG:		cp += LEN_of_ARG_REG;		break;
	  case ARG_ATM:		enter_atom(GetAtom(cp+ATM_of_ARG_ATM));
				cp += LEN_of_ARG_ATM;		break;
	  case ARG_IT:		cp += LEN_of_ARG_IT;		break;
	  case ARG_FLOT:	cp += LEN_of_ARG_FLOT;		break;
	  case ARG_LAB:		cp += LEN_of_ARG_LAB;		break;

	  case LAB:		cp += LEN_of_LAB;		break;
	  case PARITY:		cp += LEN_of_PARITY;		break;
	  case PARITY_LAB:	cp += LEN_of_PARITY_LAB;	break;
	  case PARITY_LAB_REG:	cp += LEN_of_PARITY_LAB_REG;	break;
	  case MOD_PRED_PARITY:
	    enter_atom(GetAtom(cp+MOD_of_MOD_PRED_PARITY));
	    enter_atom(GetPredID(cp+PRED_of_MOD_PRED_PARITY)&0xFFFF);
				cp += LEN_of_MOD_PRED_PARITY;	break;

	  case REG_REG_ATM:
	    enter_atom(GetAtom(cp+ATM_of_REG_REG_ATM));
				cp += LEN_of_REG_REG_ATM;   	break;
	  case REG_ARITY_ATM:
	    enter_atom(GetAtom(cp+ATM_of_REG_ARITY_ATM));
				cp += LEN_of_REG_ARITY_ATM;   	break;
	  case REG_LAB_REG_REG: cp += LEN_of_REG_LAB_REG_REG;	break;
	  case REG_REG_REP:	cp += LEN_of_REG_REG_REP;	break;
	  case ARG_REG_REP:	cp += LEN_of_ARG_REG_REP;	break;
	  case REG_IDX_REG_REP:	cp += LEN_of_REG_IDX_REG_REP;	break;

	  case JUMP_ON:	 
	    size = GetUShort(cp+SIZE_of_JUMP_ON);
	    cp += size*ELEN_of_JUMP_ON+TABLE_of_JUMP_ON;
	    AdjustPCunlessPackedCode(cp);
	    break;
	  case BRANCH_ON_A:
	    size = GetUShort(cp+SIZE_of_BRANCH_ON_A);
	    cp += TABLE_of_BRANCH_ON_A;
	    for(i=0; i<size; i++){
		enter_atom(GetAtom(cp+ATM_of_BRANCH_ON_A));
		cp += ELEN_of_BRANCH_ON_A;
	    }
	    break;
	  case BRANCH_ON_I:
	    size = GetUShort(cp+SIZE_of_BRANCH_ON_I);
	    cp += size*ELEN_of_BRANCH_ON_I+TABLE_of_BRANCH_ON_I;
	    break;    
	  case HASH_ON_A:
	    mask = GetUShort(cp+MASK_of_HASH_ON_A);
	    cp += TABLE_of_HASH_ON_A;
	    for(i=size=0; i<=mask; i++){
		size += GetUShort(cp+CNUM_of_HASH_ON_A);
		cp += TLEN_of_HASH_ON_A;
	    }
	    for(i=0; i<size; i++){
		enter_atom(GetAtom(cp+ATM_of_HASH_ON_A));
		cp += ELEN_of_HASH_ON_A;
	    }
	    break;
	  case HASH_ON_I:
	    mask = GetUShort(cp+MASK_of_HASH_ON_I);
	    cp += TABLE_of_HASH_ON_I;
	    for(i=size=0; i<=mask; i++){
		size += GetUShort(cp+CNUM_of_HASH_ON_I);
		cp += TLEN_of_HASH_ON_I;
	    }
	    cp += size*ELEN_of_HASH_ON_I;
	    break;
	  default:
	    Error("Unknown opcode occurred.");
	    PrintCons2F("   0x%x: 0x%x\n", cp, op_code);
	    exit_pdss(1);
	}
    }
    return(op_bottom);
}

static enter_atoms_in_constant_section(p, bottom)
    CELL *p, *bottom;
{
    while(p < bottom){
	if(Typeof(p) == ATOM){
	    enter_atom(Valueof(p));
	}
	p++;
    }
}

static enter_atom(atom)
    unsigned int atom;
{
    register unsigned int i;
    for(i=0; atom_id_table[i] != 0xFFFF; i++){
	if(atom == atom_id_table[i]) return;
    }
    atom_id_table[i] = atom;
}

static write_atom_table(fp)
    FILE *fp;
{
    CHAR *name;
    register unsigned int i, j, length;
    for(i=0; atom_id_table[i] != 0xFFFF; i++){
	name = atom_name(atom_id_table[i]);
	length = strlen(name)+1;
	WriteShort(length, fp);
	for(j=0; j<length; j++) WriteChar(name[j], fp);
    }
    WriteShort(0xFFFF, fp);  /* end of atom table */
}
    
static unsigned int convert_atom_id(atom)
    unsigned int atom;
{
    unsigned int i;
    for(i=0; i<ATOMMAX; i++){
	if(atom == atom_id_table[i]) break;
    }
    return(i);
}


/*************************************************************************
*   Save Module -- Write Code Body.					 *
*************************************************************************/

static write_code_body(cp, fp)
    FILE *fp;
    OBJ	 *cp;
{
    OBJ	 *module_bottom, *program_bottom, *addr, *base;
    unsigned int table_num, code_size, i;
    int	 cnst_offs;

    /**** Write Module Header ****/
    code_size = GetModPredSize(cp+MODULE_CODE_SIZE);
    table_num = GetUShort(cp+MODULE_NUMBER_OF_ENTRY);
    cnst_offs = GetRelAddr(cp+MODULE_CONSTANT_OFFSET);
    module_bottom = cp+code_size+MODULE_SIZE_LENGTH;
    if(cnst_offs == 0){
	program_bottom = module_bottom;
    }else{
	program_bottom = cp+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    WriteModPredSize(code_size, fp);
    WriteAtom(GetAtom(cp+MODULE_NAME), fp);
    WriteChar(0, fp);	/* Debug Info. */
    WriteChar(0, fp);	/* Reserved (5byte) */
    WriteShort(0, fp);
    WriteShort(0, fp);
    WriteShort(GetUShort(cp+MODULE_ENTRY_TABLE_SIZE), fp);
    WriteShort(table_num, fp);
    WriteRelAddr(cnst_offs, fp);
    cp += MODULE_HEADER_LENGTH;

    /**** Write Entry Table ****/
    base = cp;	/* base of relative address in entry table */
    cp += ENTRY_TABLE_HASH_TABLE_SIZE;
    for(i=0; i<table_num; i++){
	WriteAtom(GetPredID(cp+PRED_of_ENTRY_TABLE)&0xFFFF, fp);
	WritePredArity(GetPredID(cp+PRED_of_ENTRY_TABLE)>>16, fp);
	addr = GetAddr(cp+LAB_of_ENTRY_TABLE);
	WriteRelAddr(addr-base, fp);
	cp += ELEN_of_ENTRY_TABLE;
    }

    /**** Write Predicates ****/
    while(cp+PREDICATE_HEADER_LENGTH < program_bottom){
	cp = write_predicate(cp, fp);
    }
    AdjustPC(cp);

    /**** Write Structured Constent ****/
    if(cp < module_bottom){
	write_constant_section(cp, module_bottom, fp);
    }
}

static OBJ *write_predicate(cp, fp)
    FILE *fp;
    OBJ	 *cp;
{
    OBJ	 *op_bottom, *base;
    unsigned int code_size, op_code, size, mask, i;
    int	 special;

    /**** Write Predicate Header ****/
    code_size = GetModPredSize(cp+PREDICATE_CODE_SIZE);
    op_bottom = cp+code_size+PREDICATE_SIZE_LENGTH;
    WriteModPredSize(code_size, fp);
    WriteRelAddr(GetRelAddr(cp+PREDICATE_TO_MODULE_HEADER) ,fp);
    WriteAtom(GetAtom(cp+PREDICATE_NAME), fp);
    WritePredArity(GetPredArity(cp+PREDICATE_ARITY), fp);
    WriteChar(0, fp);	/* Debug Info. */
    WriteInt(0, fp);	/* Rcount */
    WriteInt(0, fp);	/* Scount */
    cp += PREDICATE_HEADER_LENGTH;

    /**** Write Predicate Body ****/
    while(cp < op_bottom){
	op_code = GetOpCode(cp);
	WriteOpCode(op_code, fp);
	special = NO;
	if(op_code == SPECIAL_FUNCTION_SHIFT){
	    cp++;
	    op_code = 0x100|GetOpCode(cp);
	    WriteOpCode(op_code, fp);
	    special = YES;
	}
	switch(GetInstrType(op_code)){
	  case NO_ARG:
	    cp += special ? LEN_of_2B_NO_ARG : LEN_of_NO_ARG;
	    break;
	  case REG:
	    WriteReg(GetReg(cp+REG_of_REG), fp);
	    cp += special ? LEN_of_2B_REG : LEN_of_REG;
	    break;
	  case REGS2:
	    WriteReg(GetReg(cp+RE1_of_REGS2), fp);
	    WriteReg(GetReg(cp+RE2_of_REGS2), fp);
	    cp += special ? LEN_of_2B_REGS2 : LEN_of_REGS2;
	    break;
	  case REGS3:
	    WriteReg(GetReg(cp+RE1_of_REGS3), fp);
	    WriteReg(GetReg(cp+RE2_of_REGS3), fp);
	    WriteReg(GetReg(cp+RE3_of_REGS3), fp);
	    cp += special ? LEN_of_2B_REGS3 : LEN_of_REGS3;
	    break;
	  case REGS4:
	    WriteReg(GetReg(cp+RE1_of_REGS4), fp);
	    WriteReg(GetReg(cp+RE2_of_REGS4), fp);
	    WriteReg(GetReg(cp+RE3_of_REGS4), fp);
	    WriteReg(GetReg(cp+RE4_of_REGS4), fp);
	    cp += special ? LEN_of_2B_REGS4 : LEN_of_REGS4;
	    break;
	  case REGS5:
	    WriteReg(GetReg(cp+RE1_of_REGS5), fp);
	    WriteReg(GetReg(cp+RE2_of_REGS5), fp);
	    WriteReg(GetReg(cp+RE3_of_REGS5), fp);
	    WriteReg(GetReg(cp+RE4_of_REGS5), fp);
	    WriteReg(GetReg(cp+RE5_of_REGS5), fp);
	    cp += special ? LEN_of_2B_REGS5 : LEN_of_REGS5;
	    break;
	  case REGS6:
	    WriteReg(GetReg(cp+RE1_of_REGS6), fp);
	    WriteReg(GetReg(cp+RE2_of_REGS6), fp);
	    WriteReg(GetReg(cp+RE3_of_REGS6), fp);
	    WriteReg(GetReg(cp+RE4_of_REGS6), fp);
	    WriteReg(GetReg(cp+RE5_of_REGS6), fp);
	    WriteReg(GetReg(cp+RE6_of_REGS6), fp);
	    cp += special ? LEN_of_2B_REGS6 : LEN_of_REGS6;
	    break;
	  case REGS7:
	    WriteReg(GetReg(cp+RE1_of_REGS7), fp);
	    WriteReg(GetReg(cp+RE2_of_REGS7), fp);
	    WriteReg(GetReg(cp+RE3_of_REGS7), fp);
	    WriteReg(GetReg(cp+RE4_of_REGS7), fp);
	    WriteReg(GetReg(cp+RE5_of_REGS7), fp);
	    WriteReg(GetReg(cp+RE6_of_REGS7), fp);
	    WriteReg(GetReg(cp+RE7_of_REGS7), fp);
	    cp += special ? LEN_of_2B_REGS7 : LEN_of_REGS7;
	    break;
	  case REGS8:
	    WriteReg(GetReg(cp+RE1_of_REGS8), fp);
	    WriteReg(GetReg(cp+RE2_of_REGS8), fp);
	    WriteReg(GetReg(cp+RE3_of_REGS8), fp);
	    WriteReg(GetReg(cp+RE4_of_REGS8), fp);
	    WriteReg(GetReg(cp+RE5_of_REGS8), fp);
	    WriteReg(GetReg(cp+RE6_of_REGS8), fp);
	    WriteReg(GetReg(cp+RE7_of_REGS8), fp);
	    WriteReg(GetReg(cp+RE8_of_REGS8), fp);
	    cp += special ? LEN_of_2B_REGS8 : LEN_of_REGS8;
	    break;

	  case REG_ATM:
	    WriteReg(GetReg(cp+REG_of_REG_ATM), fp);
	    WriteAtom(GetAtom(cp+ATM_of_REG_ATM), fp);
	    cp += LEN_of_REG_ATM;
	    break;
	  case REG_ATM_LAB:
	    WriteReg(GetReg(cp+REG_of_REG_ATM_LAB), fp);
	    WriteAtom(GetAtom(cp+ATM_of_REG_ATM_LAB), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_REG_ATM_LAB), fp);
	    cp += LEN_of_REG_ATM_LAB;
	    break;
	  case REG_IT:
	    WriteReg(GetReg(cp+REG_of_REG_IT), fp);
	    WriteInt(GetInt(cp+IT_of_REG_IT), fp);
	    cp += LEN_of_REG_IT;
	    break;
	  case REG_IT_LAB:
	    WriteReg(GetReg(cp+REG_of_REG_IT_LAB), fp);
	    WriteInt(GetInt(cp+IT_of_REG_IT_LAB), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_REG_IT_LAB), fp);
	    cp += LEN_of_REG_IT_LAB;
	    break;
	  case REG_FLOT:
	    WriteReg(GetReg(cp+REG_of_REG_FLOT), fp);
	    WriteFloat(GetFloat(cp+FLOT_of_REG_FLOT), fp);
	    cp += LEN_of_REG_FLOT;
	    break;
	  case REG_FLOT_LAB:
	    WriteReg(GetReg(cp+REG_of_REG_FLOT_LAB), fp);
	    WriteFloat(GetFloat(cp+FLOT_of_REG_FLOT_LAB), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_REG_FLOT_LAB), fp);
	    cp += LEN_of_REG_FLOT_LAB;
	    break;
	  case REG_ARITY:
	    WriteReg(GetReg(cp+REG_of_REG_ARITY), fp);
	    WriteArity(GetArity(cp+ARITY_of_REG_ARITY), fp);
	    cp += LEN_of_REG_ARITY;
	    break;
	  case REG_ARITY_LAB:
	    WriteReg(GetReg(cp+REG_of_REG_ARITY_LAB), fp);
	    WriteArity(GetArity(cp+ARITY_of_REG_ARITY_LAB), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_REG_ARITY_LAB), fp);
	    cp += LEN_of_REG_ARITY_LAB;
	    break;
	  case REG_LAB:
	    WriteReg(GetReg(cp+REG_of_REG_LAB), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_REG_LAB), fp);
	    cp += LEN_of_REG_LAB;
	    break;
	  case REG_LAB6:
	    WriteReg(GetReg(cp+REG_of_REG_LAB6), fp);
	    WriteRelAddr(GetRelAddr(cp+LB1_of_REG_LAB6), fp);
	    WriteRelAddr(GetRelAddr(cp+LB2_of_REG_LAB6), fp);
	    WriteRelAddr(GetRelAddr(cp+LB3_of_REG_LAB6), fp);
	    WriteRelAddr(GetRelAddr(cp+LB4_of_REG_LAB6), fp);
	    WriteRelAddr(GetRelAddr(cp+LB5_of_REG_LAB6), fp);
	    WriteRelAddr(GetRelAddr(cp+LB6_of_REG_LAB6), fp);
	    cp += LEN_of_REG_LAB6;
	    break;

	  case REG_IDX:
	    WriteReg(GetReg(cp+REG_of_REG_IDX), fp);
	    WriteIndex(GetIndex(cp+IDX_of_REG_IDX), fp);
	    cp += LEN_of_REG_IDX;
	    break;
	  case REG_IDX_REG:
	    WriteReg(GetReg(cp+REG_of_REG_IDX_REG), fp);
	    WriteIndex(GetIndex(cp+IDX_of_REG_IDX_REG), fp);
	    WriteReg(GetReg(cp+RE2_of_REG_IDX_REG), fp);
	    cp += LEN_of_REG_IDX_REG;
	    break;
	  case REG_IDX_ATM:
	    WriteReg(GetReg(cp+REG_of_REG_IDX_ATM), fp);
	    WriteIndex(GetIndex(cp+IDX_of_REG_IDX_ATM), fp);
	    WriteAtom(GetAtom(cp+ATM_of_REG_IDX_ATM), fp);
	    cp += LEN_of_REG_IDX_ATM;
	    break;
	  case REG_IDX_IT:
	    WriteReg(GetReg(cp+REG_of_REG_IDX_IT), fp);
	    WriteIndex(GetIndex(cp+IDX_of_REG_IDX_IT), fp);
	    WriteInt(GetInt(cp+IT_of_REG_IDX_IT), fp);
	    cp += LEN_of_REG_IDX_IT;
	    break;
	  case REG_IDX_FLOT:
	    WriteReg(GetReg(cp+REG_of_REG_IDX_FLOT), fp);
	    WriteIndex(GetIndex(cp+IDX_of_REG_IDX_FLOT), fp);
	    WriteFloat(GetFloat(cp+FLOT_of_REG_IDX_FLOT), fp);
	    cp += LEN_of_REG_IDX_FLOT;
	    break;

	  case ARG:
	    WriteReg(GetReg(cp+ARG_of_ARG), fp);
	    cp += LEN_of_ARG;
	    break;
	  case ARG_REG:
	    WriteReg(GetReg(cp+ARG_of_ARG_REG), fp);
	    WriteReg(GetReg(cp+REG_of_ARG_REG), fp);
	    cp += LEN_of_ARG_REG;
	    break;
	  case ARG_ATM:
	    WriteReg(GetReg(cp+ARG_of_ARG_ATM), fp);
	    WriteAtom(GetAtom(cp+ATM_of_ARG_ATM), fp);
	    cp += LEN_of_ARG_ATM;
	    break;
	  case ARG_IT:
	    WriteReg(GetReg(cp+ARG_of_ARG_IT), fp);
	    WriteInt(GetInt(cp+IT_of_ARG_IT), fp);
	    cp += LEN_of_ARG_IT;
	    break;
	  case ARG_FLOT:
	    WriteReg(GetReg(cp+ARG_of_ARG_FLOT), fp);
	    WriteFloat(GetFloat(cp+FLOT_of_ARG_FLOT), fp);
	    cp += LEN_of_ARG_FLOT;
	    break;
	  case ARG_LAB:
	    WriteReg(GetReg(cp+ARG_of_ARG_LAB), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_ARG_LAB), fp);
	    cp += LEN_of_ARG_LAB;
	    break;

	  case LAB:
	    WriteRelAddr(GetRelAddr(cp+LAB_of_LAB), fp);
	    cp += LEN_of_LAB;
	    break;
	  case PARITY:
	    WritePredArity(GetPredArity(cp+PARITY_of_PARITY), fp);
	    cp += LEN_of_PARITY;
	    break;
	  case PARITY_LAB:
	    WritePredArity(GetPredArity(cp+PARITY_of_PARITY_LAB), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_PARITY_LAB), fp);
	    cp += LEN_of_PARITY_LAB;
	    break;
	  case PARITY_LAB_REG:
	    WritePredArity(GetPredArity(cp+PARITY_of_PARITY_LAB_REG), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_PARITY_LAB_REG), fp);
	    WriteReg(GetReg(cp+REG_of_PARITY_LAB_REG), fp);
	    cp += LEN_of_PARITY_LAB_REG;
	    break;
	  case MOD_PRED_PARITY:
	    WriteAtom(GetAtom(cp+MOD_of_MOD_PRED_PARITY), fp);
	    WriteAtom(GetPredID(cp+PRED_of_MOD_PRED_PARITY)&0xFFFF, fp);
	    WritePredArity(GetPredArity(cp+PARITY_of_MOD_PRED_PARITY), fp);
	    cp += LEN_of_MOD_PRED_PARITY;
	    break;

	  case REG_REG_ATM:
	    WriteReg(GetReg(cp+REG_of_REG_REG_ATM), fp);
	    WriteReg(GetReg(cp+RE2_of_REG_REG_ATM), fp);
	    WriteAtom(GetAtom(cp+ATM_of_REG_REG_ATM), fp);
	    cp += LEN_of_REG_REG_ATM;
	    break;
	  case REG_ARITY_ATM:
	    WriteReg(GetReg(cp+REG_of_REG_ARITY_ATM), fp);
	    WriteArity(GetArity(cp+ARITY_of_REG_ARITY_ATM), fp);
	    WriteAtom(GetAtom(cp+ATM_of_REG_ARITY_ATM), fp);
	    cp += LEN_of_REG_ARITY_ATM;
	    break;
	  case REG_LAB_REG_REG:
	    WriteReg(GetReg(cp+REG_of_REG_LAB_REG_REG), fp);
	    WriteRelAddr(GetRelAddr(cp+LAB_of_REG_LAB_REG_REG), fp);
	    WriteReg(GetReg(cp+RE2_of_REG_LAB_REG_REG), fp);
	    WriteReg(GetReg(cp+RE3_of_REG_LAB_REG_REG), fp);
	    cp += LEN_of_REG_LAB_REG_REG;
	    break;
	  case REG_REG_REP:
	    WriteReg(GetReg(cp+REG_of_REG_REG_REP), fp);
	    WriteReg(GetReg(cp+RE2_of_REG_REG_REP), fp);
	    WriteRepnum(GetRepnum(cp+REP_of_REG_REG_REP), fp);
	    cp += LEN_of_REG_REG_REP;
	    break;
	  case ARG_REG_REP:
	    WriteReg(GetReg(cp+ARG_of_ARG_REG_REP), fp);
	    WriteReg(GetReg(cp+REG_of_ARG_REG_REP), fp);
	    WriteRepnum(GetRepnum(cp+REP_of_ARG_REG_REP), fp);
	    cp += LEN_of_ARG_REG_REP;
	    break;
	  case REG_IDX_REG_REP:
	    WriteReg(GetReg(cp+REG_of_REG_IDX_REG_REP), fp);
	    WriteIndex(GetIndex(cp+IDX_of_REG_IDX_REG_REP), fp);
	    WriteReg(GetReg(cp+RE2_of_REG_IDX_REG_REP), fp);
	    WriteRepnum(GetRepnum(cp+REP_of_REG_IDX_REG_REP), fp);
	    cp += LEN_of_REG_IDX_REG_REP;
	    break;

	  case JUMP_ON:
	    WriteReg(GetReg(cp+REG_of_JUMP_ON), fp);
	    size = GetUShort(cp+SIZE_of_JUMP_ON);
	    WriteShort(size, fp);
	    WriteRelAddr(GetRelAddr(cp+FAIL_of_JUMP_ON), fp);
	    cp += TABLE_of_JUMP_ON;
	    while(size--){
		WriteRelAddr(GetRelAddr(cp+LAB_of_JUMP_ON), fp);
		cp += ELEN_of_JUMP_ON;
	    }
	    AdjustPCunlessPackedCode(cp);
	    break;
	  case BRANCH_ON_A:
	    WriteReg(GetReg(cp+REG_of_BRANCH_ON_A), fp);
	    size = GetUShort(cp+SIZE_of_BRANCH_ON_A);
	    WriteShort(size, fp);
	    WriteRelAddr(GetRelAddr(cp+FAIL_of_BRANCH_ON_A), fp);
	    cp += TABLE_of_BRANCH_ON_A;
	    while(size--){
		WriteAtom(GetAtom(cp+ATM_of_BRANCH_ON_A), fp);
		WriteRelAddr(GetRelAddr(cp+LAB_of_BRANCH_ON_A), fp);
		cp += ELEN_of_BRANCH_ON_A;
	    }
	    break;
	  case BRANCH_ON_I:
	    WriteReg(GetReg(cp+REG_of_BRANCH_ON_I), fp);
	    size = GetUShort(cp+SIZE_of_BRANCH_ON_I);
	    WriteShort(size, fp);
	    WriteRelAddr(GetRelAddr(cp+FAIL_of_BRANCH_ON_I), fp);
	    cp += TABLE_of_BRANCH_ON_I;
	    while(size--){
		WriteInt(GetInt(cp+IT_of_BRANCH_ON_I), fp);
		WriteRelAddr(GetRelAddr(cp+LAB_of_BRANCH_ON_I), fp);
		cp += ELEN_of_BRANCH_ON_I;
	    }
	    break;
	  case HASH_ON_A:
	    base = cp;
	    WriteReg(GetReg(cp+REG_of_HASH_ON_A), fp);
	    mask = GetUShort(cp+MASK_of_HASH_ON_A);
	    WriteShort(mask, fp);
	    WriteRelAddr(GetRelAddr(cp+FAIL_of_HASH_ON_A), fp);
	    cp += TABLE_of_HASH_ON_A;
	    for(i=size=0; i<=mask; i++){
		size += GetUShort(cp+CNUM_of_HASH_ON_A);
		cp += TLEN_of_HASH_ON_A;
	    }
	    WriteShort(size, fp);
	    while(size--){
		WriteAtom(GetAtom(cp+ATM_of_HASH_ON_A), fp);
		WriteRelAddr(GetAddr(cp+LAB_of_HASH_ON_A)-base, fp);
		cp += ELEN_of_HASH_ON_A;
	    }
	    break;
	  case HASH_ON_I:
	    base = cp;
	    WriteReg(GetReg(cp+REG_of_HASH_ON_I), fp);
	    mask = GetUShort(cp+MASK_of_HASH_ON_I);
	    WriteShort(mask, fp);
	    WriteRelAddr(GetRelAddr(cp+FAIL_of_HASH_ON_I), fp);
	    cp += TABLE_of_HASH_ON_I;
	    for(i=size=0; i<=mask; i++){
		size += GetUShort(cp+CNUM_of_HASH_ON_I);
		cp += TLEN_of_HASH_ON_I;
	    }
	    WriteShort(size, fp);
	    while(size--){
		WriteInt(GetInt(cp+IT_of_HASH_ON_I), fp);
		WriteRelAddr(GetAddr(cp+LAB_of_HASH_ON_I)-base, fp);
		cp += ELEN_of_HASH_ON_I;
	    }
	    break;
	}
    }
    return(op_bottom);
}

static write_constant_section(p, bottom, fp)
    CELL *p, *bottom;
    FILE *fp;
{
    while(p < bottom){
	switch(Typeof(p)){
	  case ATOM:
	    WriteChar(Typeof(p), fp);
	    WriteAtom(Valueof(p), fp);
	    break;
	  case INT:
	  case FLOAT:
	  case DESC:
	    WriteChar(Typeof(p), fp);
	    WriteLong(Valueof(p), fp);
	    break;
	  case LIST:
	  case VECTOR:
	  case STRING:
	  case 0xFF:
	    WriteChar(Typeof(p), fp);
	    WriteLong(Valueof(p)-((int)p), fp);
	    break;
	}
	p++;
    }
}


/*************************************************************************
*   Load Module -- Macros / Subroutine.					 *
*************************************************************************/

static unsigned short get2c(fp)
    FILE *fp;
{
    register unsigned short s;
    s = getc(fp);
    s = getc(fp)|(s<<8);
    return(s);
}

static unsigned int get4c(fp)
    FILE *fp;
{
    register unsigned int l;
    l = getc(fp);
    l = getc(fp)|(l<<8);
    l = getc(fp)|(l<<8);
    l = getc(fp)|(l<<8);
    return(l);
}

static short get2sc(fp)
    FILE *fp;
{
    register short s;
    s = getc(fp);
    s = getc(fp)|(s<<8);
    return(s);
}

static int get4sc(fp)
    FILE *fp;
{
    register int l;
    l = getc(fp);
    l = getc(fp)|(l<<8);
    l = getc(fp)|(l<<8);
    l = getc(fp)|(l<<8);
    return(l);
}

#define ReadOpCode(fp)		getc(fp)
#define ReadReg(fp)		getc(fp)
#define ReadAtom(fp)		atom_id_table[get2c(fp)]
#define ReadInt(fp)		get4sc(fp)
#define ReadFloat(fp)		get4sc(fp)
#define ReadArity(fp)		getc(fp)
#define ReadIndex(fp)		getc(fp)
#define ReadRepnum(fp)		getc(fp)
#define ReadPredArity(fp)	getc(fp)
#define ReadPredID(fp)		get4c(fp)
#if KLB_4BYTE_REL_ADDR
#define ReadRelAddr(fp)		get4sc(fp)
#define ReadModPredSize(fp)	get4c(fp)
#else
#define ReadRelAddr(fp)		get2sc(fp)
#define ReadModPredSize(fp)	get2c(fp)
#endif
#define ReadChar(fp)		get1sc(fp)
#define ReadShort(fp)		get2sc(fp)
#define ReadLong(fp)		get4sc(fp)
#define ReadUChar(fp)		getc(fp)
#define ReadUShort(fp)		get2c(fp)
#define ReadULong(fp)		get4c(fp)

struct hash_on_entry{
    struct hash_on_entry *next;
    int	 constant;
    int	 label;
};
	
struct hash_table{
    struct hash_on_entry *head;
    struct hash_on_entry *tail;
    unsigned int collision;
};

static struct hash_table *read_hash_table_atom();
static struct hash_table *read_hash_table_int();
static struct hash_table *read_entry_table();
static OBJ *put_hash_table_atom();
static OBJ *put_hash_table_int();
static OBJ *put_entry_table();
static OBJ *read_predicate();


/*************************************************************************
*   Load Module -- Main.						 *
**************************************************************************

Return Value:
  LOAD_SUCCESS		= 0 -> Success.
  LOAD_NOT_SAV_FILE	= 1 -> Failure, Not PDSS SAV File.
  LOAD_BAD_VERSION	= 2 -> Failure, Not Compatible Version.
  LOAD_ERROR		= 3 -> Failure, Some Error.
  LOAD_MODULE_PROTECTED = 4 -> Failure, Cannot Update Module.
  LOAD_REQUEST_GC	= 5 -> Failure, Request GC.
			       Call once more after code area GC.
*/

int load_module(fp, module)
    FILE *fp;
    MODULE_ENTRY **module;
{   
    unsigned int module_id, module_size, f;
    if(ReadUShort(fp) != SAV_MAGIC){
	Error("\n>>> Loader: Not PDSS SAV File.");
	return(LOAD_NOT_SAV_FILE);
    }
    if(ReadUChar(fp) != SAV_VRSON1){
	Error("\n>>> Loader: Not Compatible Version.");
	return(LOAD_BAD_VERSION);
    }
    if(ReadUChar(fp) > SAV_VRSON2){
	Error("\n>>> Loader: Not Compatible Version.");
	return(LOAD_BAD_VERSION);
    }
    read_atom_table(fp);
    AdjustPC(C);
    f = read_code_body(C, fp);
    if(f) return(f);
    module_id = GetModuleName(C);
    module_size = GetModuleSize(C)+MODULE_SIZE_LENGTH;
    if(enter_module(module_id, C, module_size, module) != MODMAN_SUCCESS){
	return(LOAD_MODULE_PROTECTED);
    }
    C += module_size;
    return(LOAD_SUCCESS);
}

static read_atom_table(fp)
    FILE *fp;
{
    register unsigned st_size, i, j;
    CHAR name[1024];

    /**** Initialize Atom ID Convert Table ****/
    for(i=0; i<ATOMMAX; i++) atom_id_table[i] = 0xFFFF;

    /**** Read Atom ID Convert Table ****/
    i=0;
    while((st_size = ReadUShort(fp)) != 0xFFFF){
	for(j=0; j<st_size; j++) name[j] = ReadUChar(fp);
	atom_id_table[i] = intern_atom(name);
	i++;
    }
}

static read_code_body(cp, fp)
    FILE *fp;
    OBJ *cp;
{ 
    OBJ *module_bottom, *program_bottom, *base;
    unsigned int code_size, table_num;
    int cnst_offs;
    struct hash_table *h_table;

    /**** Read Module Header ****/
    PutModPredSize(ReadModPredSize(fp), cp+MODULE_CODE_SIZE);
    PutAtom(ReadAtom(fp), cp+MODULE_NAME);
    PutChar(ReadUChar(fp), cp+MODULE_DEBUG_INFO);
    PutChar(ReadUChar(fp), cp+MODULE_RESERVED_1);
    PutShort(ReadUShort(fp), cp+MODULE_RESERVED_2);
    PutShort(ReadUShort(fp), cp+MODULE_RESERVED_3);
    PutShort(ReadUShort(fp), cp+MODULE_ENTRY_TABLE_SIZE);
    PutShort(ReadUShort(fp), cp+MODULE_NUMBER_OF_ENTRY);
    PutRelAddr(ReadRelAddr(fp), cp+MODULE_CONSTANT_OFFSET);
    code_size = GetModPredSize(cp+MODULE_CODE_SIZE);
    if(CodeRest() <= code_size){
	Warning("\n>>> Loader: Request GC.");
	SetCodeGcFlag();
	return(LOAD_REQUEST_GC);
    }
    table_num = GetUShort(cp+MODULE_NUMBER_OF_ENTRY);
    cnst_offs = GetRelAddr(cp+MODULE_CONSTANT_OFFSET);
    module_bottom = cp+code_size+MODULE_SIZE_LENGTH;
    if(cnst_offs == 0){
	program_bottom = module_bottom;
    }else{
	program_bottom = cp+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    cp += MODULE_HEADER_LENGTH;

    /**** Read Entry Table ****/
    base = cp;
    h_table = read_entry_table(fp, table_num);
    cp = put_entry_table(cp, base, h_table);

    /**** Read Predicates ****/
    while(cp+PREDICATE_HEADER_LENGTH < program_bottom){
	cp = read_predicate(cp, fp);
	if(cp == NULL) return(LOAD_ERROR);
    }
    AdjustPC(cp);

    /**** Read Structured Constant ****/
    if(cp < module_bottom){
	return(read_constant_section(cp, module_bottom, fp));
    }
    return(LOAD_SUCCESS);
}

static OBJ *read_predicate(cp, fp)
    FILE *fp;
    OBJ *cp;
{
    OBJ	 *op_bottom, *base;
    unsigned int code_size, op_code, pred, parity, size, mask, special;
    struct hash_table *h_table;

    /**** Read Predicate Header ****/
    PutModPredSize(ReadModPredSize(fp), cp+PREDICATE_CODE_SIZE);
    PutRelAddr(ReadRelAddr(fp), cp+PREDICATE_TO_MODULE_HEADER);
    code_size = GetModPredSize(cp+PREDICATE_CODE_SIZE);
    op_bottom = cp+code_size+PREDICATE_SIZE_LENGTH;
    PutAtom(ReadAtom(fp), cp+PREDICATE_NAME);
    PutPredArity(ReadPredArity(fp), cp+PREDICATE_ARITY);
    PutChar(ReadUChar(fp), cp+PREDICATE_DEBUG_INFO);
    PutLong(ReadULong(fp), cp+PREDICATE_RCOUNT);
    PutLong(ReadULong(fp), cp+PREDICATE_SCOUNT);
    cp += PREDICATE_HEADER_LENGTH;

    /**** Read Predicate Body ****/
    while(cp < op_bottom){
	op_code = ReadOpCode(fp);
	special = NO;
	if(op_code == SPECIAL_FUNCTION_SHIFT){
	    PutOpCode(SPECIAL_FUNCTION_SHIFT, cp); cp++;
	    op_code = 0x100|ReadOpCode(fp);
	    special = YES;
	}
	PutOpCode(op_code, cp);
	switch(GetInstrType(op_code)){
	  case NO_ARG:
	    cp += special ? LEN_of_2B_NO_ARG : LEN_of_NO_ARG;
	    break;
	  case REG:
	    PutReg(ReadReg(fp), cp+REG_of_REG);
	    cp += special ? LEN_of_2B_REG : LEN_of_REG;
	    break;
	  case REGS2:
	    PutReg(ReadReg(fp), cp+RE1_of_REGS2);
	    PutReg(ReadReg(fp), cp+RE2_of_REGS2);
	    cp += special ? LEN_of_2B_REGS2 : LEN_of_REGS2;
	    break;
	  case REGS3:
	    PutReg(ReadReg(fp), cp+RE1_of_REGS3);
	    PutReg(ReadReg(fp), cp+RE2_of_REGS3);
	    PutReg(ReadReg(fp), cp+RE3_of_REGS3);
	    cp += special ? LEN_of_2B_REGS3 : LEN_of_REGS3;
	    break;
	  case REGS4:
	    PutReg(ReadReg(fp), cp+RE1_of_REGS4);
	    PutReg(ReadReg(fp), cp+RE2_of_REGS4);
	    PutReg(ReadReg(fp), cp+RE3_of_REGS4);
	    PutReg(ReadReg(fp), cp+RE4_of_REGS4);
	    cp += special ? LEN_of_2B_REGS4 : LEN_of_REGS4;
	    break;
	  case REGS5:
	    PutReg(ReadReg(fp), cp+RE1_of_REGS5);
	    PutReg(ReadReg(fp), cp+RE2_of_REGS5);
	    PutReg(ReadReg(fp), cp+RE3_of_REGS5);
	    PutReg(ReadReg(fp), cp+RE4_of_REGS5);
	    PutReg(ReadReg(fp), cp+RE5_of_REGS5);
	    cp += special ? LEN_of_2B_REGS5 : LEN_of_REGS5;
	    break;
	  case REGS6:
	    PutReg(ReadReg(fp), cp+RE1_of_REGS6);
	    PutReg(ReadReg(fp), cp+RE2_of_REGS6);
	    PutReg(ReadReg(fp), cp+RE3_of_REGS6);
	    PutReg(ReadReg(fp), cp+RE4_of_REGS6);
	    PutReg(ReadReg(fp), cp+RE5_of_REGS6);
	    PutReg(ReadReg(fp), cp+RE6_of_REGS6);
	    cp += special ? LEN_of_2B_REGS6 : LEN_of_REGS6;
	    break;
	  case REGS7:
	    PutReg(ReadReg(fp), cp+RE1_of_REGS7);
	    PutReg(ReadReg(fp), cp+RE2_of_REGS7);
	    PutReg(ReadReg(fp), cp+RE3_of_REGS7);
	    PutReg(ReadReg(fp), cp+RE4_of_REGS7);
	    PutReg(ReadReg(fp), cp+RE5_of_REGS7);
	    PutReg(ReadReg(fp), cp+RE6_of_REGS7);
	    PutReg(ReadReg(fp), cp+RE7_of_REGS7);
	    cp += special ? LEN_of_2B_REGS7 : LEN_of_REGS7;
	    break;
	  case REGS8:
	    PutReg(ReadReg(fp), cp+RE1_of_REGS8);
	    PutReg(ReadReg(fp), cp+RE2_of_REGS8);
	    PutReg(ReadReg(fp), cp+RE3_of_REGS8);
	    PutReg(ReadReg(fp), cp+RE4_of_REGS8);
	    PutReg(ReadReg(fp), cp+RE5_of_REGS8);
	    PutReg(ReadReg(fp), cp+RE6_of_REGS8);
	    PutReg(ReadReg(fp), cp+RE7_of_REGS8);
	    PutReg(ReadReg(fp), cp+RE8_of_REGS8);
	    cp += special ? LEN_of_2B_REGS8 : LEN_of_REGS8;
	    break;

	  case REG_ATM:
	    PutReg(ReadReg(fp), cp+REG_of_REG_ATM);
	    PutAtom(ReadAtom(fp), cp+ATM_of_REG_ATM);
	    cp += LEN_of_REG_ATM;
	    break;
	  case REG_ATM_LAB:
	    PutReg(ReadReg(fp), cp+REG_of_REG_ATM_LAB);
	    PutAtom(ReadAtom(fp), cp+ATM_of_REG_ATM_LAB);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_REG_ATM_LAB);
	    cp += LEN_of_REG_ATM_LAB;
	    break;
	  case REG_IT:
	    PutReg(ReadReg(fp), cp+REG_of_REG_IT);
	    PutInt(ReadInt(fp), cp+IT_of_REG_IT);
	    cp += LEN_of_REG_IT;
	    break;
	  case REG_IT_LAB:
	    PutReg(ReadReg(fp), cp+REG_of_REG_IT_LAB);
	    PutInt(ReadInt(fp), cp+IT_of_REG_IT_LAB);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_REG_IT_LAB);
	    cp += LEN_of_REG_IT_LAB;
	    break;
	  case REG_FLOT:
	    PutReg(ReadReg(fp), cp+REG_of_REG_FLOT);
	    PutFloat(ReadFloat(fp), cp+FLOT_of_REG_FLOT);
	    cp += LEN_of_REG_FLOT;
	    break;
	  case REG_FLOT_LAB:
	    PutReg(ReadReg(fp), cp+REG_of_REG_FLOT_LAB);
	    PutFloat(ReadFloat(fp), cp+FLOT_of_REG_FLOT_LAB);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_REG_FLOT_LAB);
	    cp += LEN_of_REG_FLOT_LAB;
	    break;
	  case REG_ARITY:
	    PutReg(ReadReg(fp), cp+REG_of_REG_ARITY);
	    PutArity(ReadArity(fp), cp+ARITY_of_REG_ARITY);
	    cp += LEN_of_REG_ARITY;
	    break;
	  case REG_ARITY_LAB:
	    PutReg(ReadReg(fp), cp+REG_of_REG_ARITY_LAB);
	    PutArity(ReadArity(fp), cp+ARITY_of_REG_ARITY_LAB);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_REG_ARITY_LAB);
	    cp += LEN_of_REG_ARITY_LAB;
	    break;
	  case REG_LAB:
	    PutReg(ReadReg(fp), cp+REG_of_REG_LAB);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_REG_LAB);
	    cp += LEN_of_REG_LAB;
	    break;
	  case REG_LAB6:
	    PutReg(ReadReg(fp), cp+REG_of_REG_LAB6);
	    PutRelAddr(ReadRelAddr(fp), cp+LB1_of_REG_LAB6);
	    PutRelAddr(ReadRelAddr(fp), cp+LB2_of_REG_LAB6);
	    PutRelAddr(ReadRelAddr(fp), cp+LB3_of_REG_LAB6);
	    PutRelAddr(ReadRelAddr(fp), cp+LB4_of_REG_LAB6);
	    PutRelAddr(ReadRelAddr(fp), cp+LB5_of_REG_LAB6);
	    PutRelAddr(ReadRelAddr(fp), cp+LB6_of_REG_LAB6);
	    cp += LEN_of_REG_LAB6;
	    break;

	  case REG_IDX:
	    PutReg(ReadReg(fp), cp+REG_of_REG_IDX);
	    PutIndex(ReadIndex(fp), cp+IDX_of_REG_IDX);
	    cp += LEN_of_REG_IDX;
	    break;
	  case REG_IDX_REG:
	    PutReg(ReadReg(fp), cp+REG_of_REG_IDX_REG);
	    PutIndex(ReadIndex(fp), cp+IDX_of_REG_IDX_REG);
	    PutReg(ReadReg(fp), cp+RE2_of_REG_IDX_REG);
	    cp += LEN_of_REG_IDX_REG;
	    break;
	  case REG_IDX_ATM:
	    PutReg(ReadReg(fp), cp+REG_of_REG_IDX_ATM);
	    PutIndex(ReadIndex(fp), cp+IDX_of_REG_IDX_ATM);
	    PutAtom(ReadAtom(fp), cp+ATM_of_REG_IDX_ATM);
	    cp += LEN_of_REG_IDX_ATM;
	    break;
	  case REG_IDX_IT:
	    PutReg(ReadReg(fp), cp+REG_of_REG_IDX_IT);
	    PutIndex(ReadIndex(fp), cp+IDX_of_REG_IDX_IT);
	    PutInt(ReadInt(fp), cp+IT_of_REG_IDX_IT);
	    cp += LEN_of_REG_IDX_IT;
	    break;
	  case REG_IDX_FLOT:
	    PutReg(ReadReg(fp), cp+REG_of_REG_IDX_FLOT);
	    PutIndex(ReadIndex(fp), cp+IDX_of_REG_IDX_FLOT);
	    PutFloat(ReadFloat(fp), cp+FLOT_of_REG_IDX_FLOT);
	    cp += LEN_of_REG_IDX_FLOT;
	    break;
	    
	  case ARG:
	    PutReg(ReadReg(fp), cp+ARG_of_ARG);
	    cp += LEN_of_ARG;
	    break;
	  case ARG_REG:
	    PutReg(ReadReg(fp), cp+ARG_of_ARG_REG);
	    PutReg(ReadReg(fp), cp+REG_of_ARG_REG);
	    cp += LEN_of_ARG_REG;
	    break;
	  case ARG_ATM:
	    PutReg(ReadReg(fp), cp+ARG_of_ARG_ATM);
	    PutAtom(ReadAtom(fp), cp+ATM_of_ARG_ATM);
	    cp += LEN_of_ARG_ATM;
	    break;
	  case ARG_IT:
	    PutReg(ReadReg(fp), cp+ARG_of_ARG_IT);
	    PutInt(ReadInt(fp), cp+IT_of_ARG_IT);
	    cp += LEN_of_ARG_IT;
	    break;
	  case ARG_FLOT:
	    PutReg(ReadReg(fp), cp+ARG_of_ARG_FLOT);
	    PutFloat(ReadFloat(fp), cp+FLOT_of_ARG_FLOT);
	    cp += LEN_of_ARG_FLOT;
	    break;
	  case ARG_LAB:
	    PutReg(ReadReg(fp), cp+ARG_of_ARG_LAB);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_ARG_LAB);
	    cp += LEN_of_ARG_LAB;
	    break;

	  case LAB:
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_LAB);
	    cp += LEN_of_LAB;
	    break;
	  case PARITY:
	    PutPredArity(ReadPredArity(fp), cp+PARITY_of_PARITY);
	    cp += LEN_of_PARITY;
	    break;
	  case PARITY_LAB:
	    PutPredArity(ReadPredArity(fp), cp+PARITY_of_PARITY_LAB);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_PARITY_LAB);
	    cp += LEN_of_PARITY_LAB;
	    break;
	  case PARITY_LAB_REG:
	    PutPredArity(ReadPredArity(fp), cp+PARITY_of_PARITY_LAB_REG);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_PARITY_LAB_REG);
	    PutReg(ReadReg(fp), cp+REG_of_PARITY_LAB_REG);
	    cp += LEN_of_PARITY_LAB_REG;
	    break;
	  case MOD_PRED_PARITY:
	    PutAtom(ReadAtom(fp), cp+MOD_of_MOD_PRED_PARITY);
	    pred = ReadAtom(fp);
	    parity = ReadPredArity(fp);
	    PutPredID(pred|(parity<<16), cp+PRED_of_MOD_PRED_PARITY);
	    PutPredArity(parity, cp+PARITY_of_MOD_PRED_PARITY);
	    cp += LEN_of_MOD_PRED_PARITY;
	    break;

	  case REG_REG_ATM:
	    PutReg(ReadReg(fp), cp+REG_of_REG_REG_ATM);
	    PutReg(ReadReg(fp), cp+RE2_of_REG_REG_ATM);
	    PutAtom(ReadAtom(fp), cp+ATM_of_REG_REG_ATM);
	    cp += LEN_of_REG_REG_ATM;
	    break;
	  case REG_ARITY_ATM:
	    PutReg(ReadReg(fp), cp+REG_of_REG_ARITY_ATM);
	    PutArity(ReadArity(fp), cp+ARITY_of_REG_ARITY_ATM);
	    PutAtom(ReadAtom(fp), cp+ATM_of_REG_ARITY_ATM);
	    cp += LEN_of_REG_ARITY_ATM;
	    break;
	  case REG_LAB_REG_REG:
	    PutReg(ReadReg(fp), cp+REG_of_REG_LAB_REG_REG);
	    PutRelAddr(ReadRelAddr(fp), cp+LAB_of_REG_LAB_REG_REG);
	    PutReg(ReadReg(fp), cp+RE2_of_REG_LAB_REG_REG);
	    PutReg(ReadReg(fp), cp+RE3_of_REG_LAB_REG_REG);
	    cp += LEN_of_REG_LAB_REG_REG;
	    break;
	  case REG_REG_REP:
	    PutReg(ReadReg(fp), cp+REG_of_REG_REG_REP);
	    PutReg(ReadReg(fp), cp+RE2_of_REG_REG_REP);
	    PutRepnum(ReadRepnum(fp), cp+REP_of_REG_REG_REP);
	    cp += LEN_of_REG_REG_REP;
	    break;
	  case ARG_REG_REP:
	    PutReg(ReadReg(fp), cp+ARG_of_ARG_REG_REP);
	    PutReg(ReadReg(fp), cp+REG_of_ARG_REG_REP);
	    PutRepnum(ReadRepnum(fp), cp+REP_of_ARG_REG_REP);
	    cp += LEN_of_ARG_REG_REP;
	    break;
	  case REG_IDX_REG_REP:
	    PutReg(ReadReg(fp), cp+REG_of_REG_IDX_REG_REP);
	    PutIndex(ReadIndex(fp), cp+IDX_of_REG_IDX_REG_REP);
	    PutReg(ReadReg(fp), cp+RE2_of_REG_IDX_REG_REP);
	    PutRepnum(ReadRepnum(fp), cp+REP_of_REG_IDX_REG_REP);
	    cp += LEN_of_REG_IDX_REG_REP;
	    break;

	  case JUMP_ON:
	    PutReg(ReadReg(fp), cp+REG_of_JUMP_ON);
	    size = ReadUShort(fp);
	    PutShort(size, cp+SIZE_of_JUMP_ON);
	    PutRelAddr(ReadRelAddr(fp), cp+FAIL_of_JUMP_ON);
	    cp += TABLE_of_JUMP_ON;
	    while(size--){
		PutRelAddr(ReadRelAddr(fp), cp+LAB_of_JUMP_ON);
		cp += ELEN_of_JUMP_ON;
	    }
	    AdjustPCunlessPackedCode(cp);
	    break;
	  case BRANCH_ON_A:
	    PutReg(ReadReg(fp), cp+REG_of_BRANCH_ON_A);
	    size = ReadUShort(fp);
	    PutShort(size, cp+SIZE_of_BRANCH_ON_A);
	    PutRelAddr(ReadRelAddr(fp), cp+FAIL_of_BRANCH_ON_A);
	    cp += TABLE_of_BRANCH_ON_A;
	    while(size--){
		PutAtom(ReadAtom(fp), cp+ATM_of_BRANCH_ON_A);
		PutRelAddr(ReadRelAddr(fp), cp+LAB_of_BRANCH_ON_A);
		cp += ELEN_of_BRANCH_ON_A;
	    }
	    break;
	  case BRANCH_ON_I:
	    PutReg(ReadReg(fp), cp+REG_of_BRANCH_ON_I);
	    size = ReadUShort(fp);
	    PutShort(size, cp+SIZE_of_BRANCH_ON_I);
	    PutRelAddr(ReadRelAddr(fp), cp+FAIL_of_BRANCH_ON_I);
	    cp += TABLE_of_BRANCH_ON_I;
	    while(size--){
		PutInt(ReadInt(fp), cp+IT_of_BRANCH_ON_I);
		PutRelAddr(ReadRelAddr(fp), cp+LAB_of_BRANCH_ON_I);
		cp += ELEN_of_BRANCH_ON_I;
	    }
	    break;
	  case HASH_ON_A:
	    base = cp;
	    PutReg(ReadReg(fp), cp+REG_of_HASH_ON_A);
	    mask = ReadUShort(fp);
	    PutShort(mask, cp+MASK_of_HASH_ON_A);
	    PutRelAddr(ReadRelAddr(fp), cp+FAIL_of_HASH_ON_A);
	    cp += TABLE_of_HASH_ON_A;
	    size = ReadUShort(fp);
	    h_table = read_hash_table_atom(fp, mask, size);
	    cp = put_hash_table_atom(cp, base, mask+1, h_table);
	    break;
	  case HASH_ON_I:
	    base = cp;
	    PutReg(ReadReg(fp), cp+REG_of_HASH_ON_I);
	    mask = ReadUShort(fp);
	    PutShort(mask, cp+MASK_of_HASH_ON_I);
	    PutRelAddr(ReadRelAddr(fp), cp+FAIL_of_HASH_ON_I);
	    cp += TABLE_of_HASH_ON_I;
	    size = ReadUShort(fp);
	    h_table = read_hash_table_int(fp, mask, size);
	    cp = put_hash_table_int(cp, base, mask+1, h_table);
	    break;
	  default:
	    Error("\n>>> Loader: Unknown opcode in savefile !?");
	    return(NULL);
	}
    }
    return(op_bottom);
}

static read_constant_section(p, bottom, fp)
    CELL *p, *bottom;
    FILE *fp;
{
    int ty, va;
    while(p < bottom){
	ty = ReadUChar(fp);
	switch(ty){
	  case ATOM:
	    va = ReadAtom(fp);
	    SetAll(p, ty, va, MRBOFF);
	    break;
	  case INT:
	  case FLOAT:
	  case DESC:
	    va = ReadLong(fp);
	    SetAll(p, ty, va, MRBOFF);
	    break;
	  case LIST:
	  case VECTOR:
	  case STRING:
	  case 0xFF:
	    va = ReadLong(fp)+((int)p);
	    SetAll(p, ty, va, MRBON);
	    break;
	  default:
	    Error("\n>>> Loader: Unknown constant type in savefile !?");
	    return(LOAD_ERROR);
	}
	p++;
    }
    return(LOAD_SUCCESS);
}


/*************************************************************************
*   Read Hash Table for Hash_On_XXX Instruction.			 *
*************************************************************************/

static struct hash_table *read_hash_table_atom(fp, mask, e_num)
    FILE *fp;
    unsigned int mask, e_num;
{
    unsigned int x, i, j;
    struct hash_table *table;
    struct hash_on_entry *entry;

    t2_free();
    table = (struct hash_table *)
	    t2_alloc((mask+1)*sizeof(struct hash_table));
    entry = (struct hash_on_entry *)
	    t2_alloc(e_num*sizeof(struct hash_on_entry));
    for(i=0; i<=mask; i++){
	table[i].head = NULL;
	table[i].tail = NULL;
	table[i].collision = 0;
    }
    for(j=0; j<e_num; j++){
	entry[j].constant = x = ReadAtom(fp);
	entry[j].label = ReadRelAddr(fp);
	entry[j].next = NULL;
	x &= mask;
	if(table[x].tail == NULL){
	    table[x].head = &entry[j];
	}else{
	    table[x].tail->next = &entry[j];
	}
	table[x].tail = &entry[j];
	table[x].collision++;
    }
    return(table);
}

static struct hash_table *read_hash_table_int(fp, mask, e_num)
    FILE *fp;
    unsigned int mask, e_num;
{
    unsigned int x, i, j;
    struct hash_table *table;
    struct hash_on_entry *entry;

    t2_free();
    table = (struct hash_table *)
	    t2_alloc((mask+1)*sizeof(struct hash_table));
    entry = (struct hash_on_entry *)
	    t2_alloc(e_num*sizeof(struct hash_on_entry));
    for(i=0; i<=mask; i++){
	table[i].head = NULL;
	table[i].tail = NULL;
	table[i].collision = 0;
    }
    for(j=0; j<e_num; j++){
	entry[j].constant = x = ReadInt(fp);
	entry[j].label = ReadRelAddr(fp);
	entry[j].next = NULL;
	x &= mask;
	if(table[x].tail == NULL){
	    table[x].head = &entry[j];
	}else{
	    table[x].tail->next = &entry[j];
	}
	table[x].tail = &entry[j];
	table[x].collision++;
    }
    return(table);
}

static OBJ *put_hash_table_atom(cp, base, h_size, h_table)
    OBJ *cp, *base;
    unsigned int h_size;
    struct hash_table *h_table;
{
    OBJ *cp2, *addr;
    unsigned int i;
    struct hash_on_entry *entry;

    cp2 = cp+h_size*TLEN_of_HASH_ON_A;
    for(i=0; i<h_size; i++){
	PutShort(h_table[i].collision, cp+CNUM_of_HASH_ON_A);
	PutRelAddr(cp2-(cp+OFST_of_HASH_ON_A), cp+OFST_of_HASH_ON_A);
	entry = h_table[i].head;
	while(h_table[i].collision--){
	    PutAtom(entry->constant, cp2+ATM_of_HASH_ON_A);
	    addr = base+entry->label;
	    PutRelAddr(addr-(cp2+LAB_of_HASH_ON_A), cp2+LAB_of_HASH_ON_A);
	    cp2 += ELEN_of_HASH_ON_A;
	    entry = entry->next;
	}
	cp += TLEN_of_HASH_ON_A;
    }
    return(cp2);
}

static OBJ *put_hash_table_int(cp, base, h_size, h_table)
    OBJ *cp, *base;
    unsigned int h_size;
    struct hash_table *h_table;
{
    OBJ *cp2, *addr;
    unsigned int i;
    struct hash_on_entry *entry;

    cp2 = cp+h_size*TLEN_of_HASH_ON_I;
    for(i=0; i<h_size; i++){
	PutShort(h_table[i].collision, cp+CNUM_of_HASH_ON_I);
	PutRelAddr(cp2-(cp+OFST_of_HASH_ON_I), cp+OFST_of_HASH_ON_I);
	entry = h_table[i].head;
	while(h_table[i].collision--){
	    PutInt(entry->constant, cp2+IT_of_HASH_ON_I);
	    addr = base+entry->label;
	    PutRelAddr(addr-(cp2+LAB_of_HASH_ON_I), cp2+LAB_of_HASH_ON_I);
	    cp2 += ELEN_of_HASH_ON_I;
	    entry = entry->next;
	}
	cp += TLEN_of_HASH_ON_I;
    }
    return(cp2);
}


/*************************************************************************
*   Read Entry Table.							 *
*************************************************************************/

static struct hash_table *read_entry_table(fp, e_num)
    FILE *fp;
    unsigned int e_num;
{
    unsigned int x,i,j;
    struct hash_table *table;
    struct hash_on_entry *entry;

    t2_free();
    table = (struct hash_table *)
	    t2_alloc((ENTRY_TABLE_HASH_MASK+1)*sizeof(struct hash_table));
    entry = (struct hash_on_entry *)
	    t2_alloc(e_num*sizeof(struct hash_on_entry));
    for(i=0;i<=ENTRY_TABLE_HASH_MASK;i++){
	table[i].head = NULL;
	table[i].tail = NULL;
	table[i].collision = 0;
    }
    for(j=0;j<e_num;j++){
	x = ReadAtom(fp);
	entry[j].constant = x = (x|ReadPredArity(fp)<<16);
	entry[j].label = ReadRelAddr(fp);
	entry[j].next = NULL;
	x = ENTRY_TABLE_HASH_FUNC(x);
	if(table[x].tail == NULL){
	    table[x].head = &entry[j];
	}else{
	    table[x].tail->next = &entry[j];
	}
	table[x].tail = &entry[j];
	table[x].collision++;
    }
    return(table);
}

static OBJ *put_entry_table(cp, base, h_table)
    OBJ *cp, *base;
    struct hash_table *h_table;
{
    OBJ *cp2, *addr;
    unsigned int i;
    struct hash_on_entry *entry;

    cp2 = cp+ENTRY_TABLE_HASH_TABLE_SIZE;
    for(i=0; i<=ENTRY_TABLE_HASH_MASK; i++){
	PutShort(h_table[i].collision, cp+CNUM_of_ENTRY_TABLE);
	PutRelAddr(cp2-(cp+OFST_of_ENTRY_TABLE), cp+OFST_of_ENTRY_TABLE);
	entry = h_table[i].head;
	while(h_table[i].collision--){
	    PutPredID(entry->constant, cp2+PRED_of_ENTRY_TABLE);
	    addr = base+entry->label;
	    PutRelAddr(addr-(cp2+LAB_of_ENTRY_TABLE), cp2+LAB_of_ENTRY_TABLE);
	    cp2 += ELEN_of_ENTRY_TABLE;
	    entry = entry->next;
	}
	cp += TLEN_of_ENTRY_TABLE;
    }
    return(cp2);
}
