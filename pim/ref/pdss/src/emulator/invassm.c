/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "klb.h"
#include "instr.h"

#if INSTRUCTION_TRACE

int inverse_assemble_one(OBJ *p, OBJ *top, CHAR *s)
{
    register struct instr_rec *op;
    register OBJ *tmp_obj;
    unsigned int opcode;
    int p0;
    
    p0 = p-top;
    opcode = GetOpCode(p);
    if(opcode == SPECIAL_FUNCTION_SHIFT){
	p++;
	opcode = 0x100|GetOpCode(p);
    }
    op = &instruction_table[opcode];
    
    if(op->type < 0){
	sprintf(s, "%06x: UNKNOWN OPCODE (0x%x)", p0, opcode);
	return 0;
    }
    
    switch(op->type){
      case NO_ARG:
	sprintf(s, "%06x: %-14s", p0, op->mnem);
	break;
      case REG:
	sprintf(s, "%06x: %-14s  R%d", p0, op->mnem, GetReg2(p+REG_of_REG));
	break;
      case REGS2:
	sprintf(s, "%06x: %-14s  R%d, R%d", p0, op->mnem,
		GetReg2(p+RE1_of_REGS2), GetReg2(p+RE2_of_REGS2));
	break;
      case REGS3:
	sprintf(s, "%06x: %-14s  R%d, R%d, R%d", p0, op->mnem,
		GetReg2(p+RE1_of_REGS3), GetReg2(p+RE2_of_REGS3),
		GetReg2(p+RE3_of_REGS3));
	break;
      case REGS4:
	sprintf(s, "%06x: %-14s  R%d, R%d, R%d, R%d", p0, op->mnem,
		GetReg2(p+RE1_of_REGS4), GetReg2(p+RE2_of_REGS4),
		GetReg2(p+RE3_of_REGS4), GetReg2(p+RE4_of_REGS4));
	break;
      case REGS5:
	sprintf(s, "%06x: %-14s  R%d, R%d, R%d, R%d, R%d", p0, op->mnem,
		GetReg2(p+RE1_of_REGS5), GetReg2(p+RE2_of_REGS5),
		GetReg2(p+RE3_of_REGS5), GetReg2(p+RE4_of_REGS5),
		GetReg2(p+RE5_of_REGS5));
	break;
      case REGS6:
	sprintf(s, "%06x: %-14s  R%d, R%d, R%d, R%d, R%d, R%d", p0, op->mnem,
		GetReg2(p+RE1_of_REGS6), GetReg2(p+RE2_of_REGS6),
		GetReg2(p+RE3_of_REGS6), GetReg2(p+RE4_of_REGS6),
		GetReg2(p+RE5_of_REGS6), GetReg2(p+RE6_of_REGS6));
	break;
      case REGS7:
	sprintf(s, "%06x: %-14s  R%d, R%d, R%d, R%d, R%d, R%d, R%d", p0,
		op->mnem,
		GetReg2(p+RE1_of_REGS7), GetReg2(p+RE2_of_REGS7),
		GetReg2(p+RE3_of_REGS7), GetReg2(p+RE4_of_REGS7),
		GetReg2(p+RE5_of_REGS7), GetReg2(p+RE6_of_REGS7),
		GetReg2(p+RE7_of_REGS7));
	break;
      case REGS8:
	sprintf(s, "%06x: %-14s  R%d, R%d, R%d, R%d, R%d, R%d, R%d, R%d", p0,
		op->mnem,
		GetReg2(p+RE1_of_REGS8), GetReg2(p+RE2_of_REGS8),
		GetReg2(p+RE3_of_REGS8), GetReg2(p+RE4_of_REGS8),
		GetReg2(p+RE5_of_REGS8), GetReg2(p+RE6_of_REGS8),
		GetReg2(p+RE7_of_REGS8), GetReg2(p+RE8_of_REGS8));
	break;
	
      case REG_ATM:
	sprintf(s, "%06x: %-14s  R%d, %s", p0, op->mnem,
		GetReg2(p+REG_of_REG_ATM),
		atom_name(GetAtom(p+ATM_of_REG_ATM)));
	break;
      case REG_ATM_LAB:
	sprintf(s, "%06x: %-14s  R%d, %s, %06x", p0, op->mnem,
		GetReg2(p+REG_of_REG_ATM_LAB),
		atom_name(GetAtom(p+ATM_of_REG_ATM_LAB)),
		GetAddr(p+LAB_of_REG_ATM_LAB)-top);
	break;
      case REG_IT:
	sprintf(s, "%06x: %-14s  R%d, %d", p0, op->mnem,
		GetReg2(p+REG_of_REG_IT), GetInt(p+IT_of_REG_IT));
	break;
      case REG_IT_LAB:
	sprintf(s, "%06x: %-14s  R%d, %d, %06x", p0, op->mnem,
		GetReg2(p+REG_of_REG_IT_LAB), GetInt(p+IT_of_REG_IT_LAB),
		GetAddr(p+LAB_of_REG_IT_LAB)-top);
	break;
      case REG_FLOT:
	sprintf(s, "%06x: %-14s  R%d, %s", p0, op->mnem,
		GetReg2(p+REG_of_REG_FLOT),
		float_to_string(&(int32_t){GetFloat(p+FLOT_of_REG_FLOT)}));
	break;
      case REG_FLOT_LAB:
	sprintf(s, "%06x: %-14s  R%d, %s, %06x", p0, op->mnem,
		GetReg2(p+REG_of_REG_FLOT_LAB),
		float_to_string(&(int32_t){GetFloat(p+FLOT_of_REG_FLOT_LAB)}),
		GetAddr(p+LAB_of_REG_FLOT_LAB)-top);
	break;
      case REG_ARITY:
	sprintf(s, "%06x: %-14s  R%d, %d", p0, op->mnem,
		GetReg2(p+REG_of_REG_ARITY), GetArity(p+ARITY_of_REG_ARITY));
	break;
      case REG_ARITY_LAB:
	sprintf(s, "%06x: %-14s  R%d, %d, %06x", p0, op->mnem,
		GetReg2(p+REG_of_REG_ARITY_LAB),
		GetArity(p+ARITY_of_REG_ARITY_LAB),
		GetAddr(p+LAB_of_REG_ARITY_LAB)-top);
	break;
      case REG_LAB:
	sprintf(s, "%06x: %-14s  R%d, %06x", p0, op->mnem,
		GetReg2(p+REG_of_REG_LAB), GetAddr(p+LAB_of_REG_LAB)-top);
	break;
      case REG_LAB6:
	sprintf(s, "%06x: %-14s  R%d, %06x, %06x, %06x, %06x, %06x, %06x",
		p0, op->mnem,
		GetReg2(p+REG_of_REG_LAB6),
		GetAddr(p+LB1_of_REG_LAB6)-top,
		GetAddr(p+LB2_of_REG_LAB6)-top,
		GetAddr(p+LB3_of_REG_LAB6)-top,
		GetAddr(p+LB4_of_REG_LAB6)-top,
		GetAddr(p+LB5_of_REG_LAB6)-top,
		GetAddr(p+LB6_of_REG_LAB6)-top);
	break;

      case REG_IDX:
	sprintf(s, "%06x: %-14s  R%d, %d", p0, op->mnem,
		GetReg2(p+REG_of_REG_IDX),
		GetIndex(p+IDX_of_REG_IDX));
	break;
      case REG_IDX_REG:
	sprintf(s,"%06x: %-14s  R%d, %d, R%d", p0, op->mnem,
		GetReg2(p+REG_of_REG_IDX_REG),
		GetIndex(p+IDX_of_REG_IDX_REG),
		GetReg2(p+RE2_of_REG_IDX_REG));
	break;
      case REG_IDX_IT:
	sprintf(s,"%06x: %-14s  R%d, %d, %d", p0, op->mnem,
		GetReg2(p+REG_of_REG_IDX_IT),
		GetIndex(p+IDX_of_REG_IDX_IT),
		GetInt(p+IT_of_REG_IDX_IT));
	break;
      case REG_IDX_FLOT:
	sprintf(s,"%06x: %-14s  R%d, %d, %s", p0, op->mnem,
		GetReg2(p+REG_of_REG_IDX_FLOT),
		GetIndex(p+IDX_of_REG_IDX_FLOT),
		float_to_string(&(int32_t){GetFloat(p+FLOT_of_REG_IDX_FLOT)}));
	break;
      case REG_IDX_ATM:
	sprintf(s,"%06x: %-14s  R%d, %d, %s", p0, op->mnem,
		GetReg2(p+REG_of_REG_IDX_ATM),
		GetIndex(p+IDX_of_REG_IDX_ATM),
		atom_name(GetAtom(p+ATM_of_REG_IDX_ATM)));
	break;
	
      case ARG:
	sprintf(s, "%06x: %-14s  G%d", p0, op->mnem, GetReg2(p+ARG_of_ARG));
	break;
      case ARG_REG:
	sprintf(s, "%06x: %-14s  G%d, R%d", p0, op->mnem,
		GetReg2(p+ARG_of_ARG_REG), GetReg2(p+REG_of_ARG_REG));
	break;
      case ARG_ATM:
	sprintf(s, "%06x: %-14s  G%d, %s", p0, op->mnem,
		GetReg2(p+ARG_of_ARG_ATM),
		atom_name(GetAtom(p+ATM_of_ARG_ATM)));
	break;
      case ARG_IT:
	sprintf(s, "%06x: %-14s  G%d, %d", p0, op->mnem,
		GetReg2(p+ARG_of_ARG_IT), GetInt(p+IT_of_ARG_IT));
	break;
      case ARG_FLOT:
	sprintf(s, "%06x: %-14s  G%d, %s", p0, op->mnem,
		GetReg2(p+ARG_of_ARG_FLOT),
		float_to_string(&(int32_t){GetFloat(p+FLOT_of_ARG_FLOT)}));
	break;
      case ARG_LAB:
	sprintf(s, "%06x: %-14s  G%d, %06x", p0, op->mnem,
		GetReg2(p+ARG_of_ARG_LAB), GetAddr(p+LAB_of_ARG_LAB)-top);
	break;
	
      case LAB:
	if(opcode == KL1B_SUSPEND){
	    tmp_obj = GetAddr(p+LAB_of_LAB);
	    sprintf(s, "%06x: %-14s  %s/%d", p0, op->mnem,
		    atom_name(GetPredicateName(tmp_obj)),
		    GetPredicateArity(tmp_obj));
	}else{
	    sprintf(s, "%06x: %-14s  %06x", p0, op->mnem,
		    GetAddr(p+LAB_of_LAB)-top);
	}
	break;
      case PARITY:
	sprintf(s, "%06x: %-14s  %d", p0, op->mnem,
		GetPredArity(p+PARITY_of_PARITY_LAB));
	break;
      case PARITY_LAB:
	sprintf(s, "%06x: %-14s  %s/%d", p0, op->mnem,
		atom_name(GetPredicateName(GetAddr(p+LAB_of_PARITY_LAB))),
		GetPredArity(p+PARITY_of_PARITY_LAB));
	break;
      case PARITY_LAB_REG:
	sprintf(s, "%06x: %-14s  %s/%d, R%d", p0, op->mnem,
		atom_name(GetPredicateName(
			      GetAddr(p+LAB_of_PARITY_LAB_REG))),
		GetPredArity(p+PARITY_of_PARITY_LAB_REG),
		GetReg2(p+REG_of_PARITY_LAB_REG));
	break;
      case MOD_PRED_PARITY:
	sprintf(s, "%06x: %-14s  %s, %s/%d", p0, op->mnem,
		atom_name(GetAtom(p+MOD_of_MOD_PRED_PARITY)),
		atom_name((GetInt(p+PRED_of_MOD_PRED_PARITY)&0xFFFF)),
		GetPredArity(p+PARITY_of_MOD_PRED_PARITY));
	break;

      case REG_REG_ATM:
	sprintf(s, "%06x: %-14s  R%d, R%d, %s", p0, op->mnem,
		GetReg2(p+REG_of_REG_REG_ATM),
		GetReg2(p+RE2_of_REG_REG_ATM),
		atom_name(GetAtom(p+ATM_of_REG_REG_ATM)));
	p += LEN_of_REG_REG_ATM;
	break;
      case REG_ARITY_ATM:
	sprintf(s, "%06x: %-14s  R%d, %d, %s", p0, op->mnem,
		GetReg2(p+REG_of_REG_ARITY_ATM),
		GetArity(p+ARITY_of_REG_ARITY_ATM),
		atom_name(GetAtom(p+ATM_of_REG_ARITY_ATM)));
	p += LEN_of_REG_ARITY_ATM;
	break;
      case REG_LAB_REG_REG:
	sprintf(s, "%06x: %-14s  R%d, %06x, R%d, R%d", p0, op->mnem,
		GetReg2(p+REG_of_REG_LAB_REG_REG),
		GetAddr(p+LAB_of_REG_LAB_REG_REG)-top,
		GetReg2(p+RE2_of_REG_LAB_REG_REG),
		GetReg2(p+RE3_of_REG_LAB_REG_REG));
	p += LEN_of_REG_LAB_REG_REG;
	break;
      case REG_REG_REP:
	sprintf(s, "%06x: %-14s  R%d, R%d, %d", p0, op->mnem,
		GetReg2(p+REG_of_REG_REG_REP),
		GetReg2(p+RE2_of_REG_REG_REP),
		GetRepnum(p+REP_of_REG_REG_REP));
	p += LEN_of_REG_REG_REP;
	break;
      case ARG_REG_REP:
	sprintf(s, "%06x: %-14s  G%d, R%d, %d", p0, op->mnem,
		GetReg2(p+ARG_of_ARG_REG_REP),
		GetReg2(p+REG_of_ARG_REG_REP),
		GetRepnum(p+REP_of_ARG_REG_REP));
	p += LEN_of_ARG_REG_REP;
	break;
      case REG_IDX_REG_REP:
	sprintf(s, "%06x: %-14s  R%d, %d, R%d, %d", p0, op->mnem,
		GetReg2(p+REG_of_REG_IDX_REG_REP),
		GetIndex(p+IDX_of_REG_IDX_REG_REP),
		GetReg2(p+RE2_of_REG_IDX_REG_REP),
		GetRepnum(p+REP_of_REG_IDX_REG_REP));
	p += LEN_of_REG_IDX_REG_REP;
	break;

      case JUMP_ON:
      case BRANCH_ON_I:
      case BRANCH_ON_A:
      case HASH_ON_I:
      case HASH_ON_A:
	sprintf(s, "%06x: %-14s  R%d, %d, %06x", p0, op->mnem,
		GetReg2(p+1), GetUShort(p+2), GetAddr(p+4)-top);
	break;
	
      default:
	sprintf(s, "%06x: UNSUPPORTED OP CODE (0x%x).\n", p0, opcode);
	break;
    }
    return 0;
}

#endif
