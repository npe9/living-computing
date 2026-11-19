// PimALU.bsv -- the E stage's 40-bit ALU and tag manipulation.
//
// The paper documents that "ALU operation and tag manipulation
// including turning on/off MRB are performed in parallel" (p.428,
// section 2.3).  This package is that parallel operation: one ALU
// result plus an independent MRB set/clear that may be applied to it.
//
// The operation *set* is model-defined; the documents name no ALU
// opcodes.  Arithmetic produces an integer-tagged word; MOV preserves
// the source tag, which is what the S/E operand path needs.

package PimALU;

import PimTypes::*;

function Word alu(AluOp op, Word a, Word b);
  Data da = wordData(a);
  Data db = wordData(b);
  case (op)
    aluAdd:     return mkWord(tagInt, False, da + db);
    aluSub:     return mkWord(tagInt, False, da - db);
    aluAnd:     return mkWord(tagType(wordTag(a)), tagMRB(wordTag(a)), da & db);
    aluOr:      return mkWord(tagType(wordTag(a)), tagMRB(wordTag(a)), da | db);
    aluXor:     return mkWord(tagType(wordTag(a)), tagMRB(wordTag(a)), da ^ db);
    aluMov:     return a;
    aluShl:     return mkWord(tagInt, False, da << db[4:0]);
    aluShr:     return mkWord(tagInt, False, da >> db[4:0]);
    aluEq:      return wordInt(da == db ? 1 : 0);
    aluNe:      return wordInt(da != db ? 1 : 0);
    aluTagSet: return mkWord(tagType(wordTag(a)), True,  da);
    aluTagClr: return mkWord(tagType(wordTag(a)), False, da);
    aluNeg:     return mkWord(tagInt, False, 0 - da);
    default:     return a;
  endcase
endfunction

endpackage
