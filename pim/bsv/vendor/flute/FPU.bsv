// Copyright (c) 2013-2019 Bluespec, Inc. All Rights Reserved
//
// Vendored from Flute (https://github.com/bluespec/Flute),
// src_Core/CPU/FPU.bsv at commit 9b2b056527429e509c719c417a588b3ea594949b,
// under the Apache License 2.0 (LICENSE beside this file).  Changed for
// the PIM/m core (pim/bsv/vendor/flute/README.md): the `ifdef's resolved
// for single precision with the divider (ISA_D off, INCLUDE_FDIV on,
// INCLUDE_FSQRT off), and the ISA_Decls import replaced by the two types
// used from it, FpuOp and Token, copied here.  Nothing else.
package FPU;

import FIFOF :: *;
import RegFile :: *;
import GetPut :: *;
import ClientServer :: *;

import FloatingPoint :: *;
import Divide :: *;
import SquareRoot ::*;

// ================================================================
// From Flute src_Core/ISA/ISA_Decls.bsv (the two declarations used here)
// Tokens are used for signalling/synchronization, and have no payload
typedef Bit #(0) Token;

typedef enum {FPAdd,
	      FPSub,
	      FPMul,
	      FPDiv,
	      FPSqrt,
	      FPMAdd,
	      FPMSub,
	      FPNMAdd,
	      FPNMSub
   } FpuOp
   deriving (Bits, Eq, FShow);

// ================================================================
// Type definitions
typedef FloatingPoint#(11,52) FDouble;
typedef FloatingPoint#(8,23)  FSingle;

typedef union tagged {
   FDouble D;
   FSingle S;
   } FloatU deriving(Bits,Eq);

typedef Tuple5#( FloatU,FloatU,FloatU,RoundMode,FpuOp) Fpu_Req;
typedef Tuple2#( FloatU, FloatingPoint::Exception )       Fpu_Rsp;

typedef Tuple2#( FSingle, FloatingPoint::Exception )      FpuR;

interface FPU_IFC;
   interface Server #( Fpu_Req, Fpu_Rsp ) server_core;

   // ---- Reset
   interface Server #(Token, Token) server_reset;
endinterface

(* synthesize *)
module mkFPU ( FPU_IFC );
   Server# (Tuple2# (UInt #(56), UInt #(28))
          , Tuple2# (UInt #(28), UInt #(28))) _div <- mkDivider(1);
   Server# (Tuple3# (FSingle, FSingle, RoundMode)
          , FpuR) fpu_div <- mkFloatingPointDivider(_div);

   Server# (Tuple4# (Maybe# (FSingle), FSingle, FSingle, RoundMode)
          , FpuR ) fpu_madd <- mkFloatingPointFusedMultiplyAccumulate;

   FIFOF #(Token)          resetReqsF           <- mkFIFOF;
   FIFOF #(Token)          resetRspsF           <- mkFIFOF;

   FIFOF#( Fpu_Req )  iFifo        <- mkFIFOF; // TODO: bypass fifos?
   FIFOF#( Fpu_Rsp )  oFifo        <- mkFIFOF; // TODO: bypass fifos?
   FIFOF#( RoundMode ) rmdFifo     <- mkFIFOF; // TODO: bypass fifos?
   FIFOF#( Bool )     isNegateFifo <- mkFIFOF; // TODO: bypass fifos?
   Reg#(FpuR)         resWire      <- mkWire;

   let x    = iFifo.first();
   let op1  = tpl_1(x);
   let op2  = tpl_2(x);
   let op3  = tpl_3(x);
   let rmd  = tpl_4(x);
   let iop  = tpl_5(x);

   FSingle opd1 = op1.S;
   FSingle opd2 = op2.S;
   FSingle opd3 = op3.S;

   rule start_op;
      iFifo.deq();

      if      (iop == FPNMAdd)    isNegateFifo.enq(True);
      else if (iop == FPNMSub)    isNegateFifo.enq(True);
      else                        isNegateFifo.enq(False);

      rmdFifo.enq(rmd);

      case ( iop )
         FPAdd:   fpu_madd.request.put (tuple4(Valid(opd1), opd2,         one(False), rmd) );
         FPSub:   fpu_madd.request.put (tuple4(Valid(opd1), negate(opd2), one(False), rmd) );
         FPMul:   fpu_madd.request.put (tuple4(Invalid,     opd1,         opd2,       rmd) );
         FPDiv:   fpu_div.request.put (tuple3 (opd1, opd2, rmd) );
         FPMAdd:  fpu_madd.request.put(  tuple4(Valid(opd3),         opd1, opd2, rmd) );
         FPMSub:  fpu_madd.request.put(  tuple4(Valid(negate(opd3)), opd1, opd2, rmd) );
         FPNMAdd: fpu_madd.request.put(  tuple4(Valid(opd3),         opd1, opd2, rmd) );
         FPNMSub: fpu_madd.request.put(  tuple4(Valid(negate(opd3)), opd1, opd2, rmd) );
      endcase

   endrule

   // rule generator for handling responses from multi-cycle pipes
   function Rules fn_genMultCycResRules (Server #(req, FpuR) pipe);
      return (rules
         rule getResFromPipe;
            let res <- pipe.response.get ();
            resWire <= res;
         endrule
      endrules);
   endfunction

   let rl_resRules = emptyRules;
   rl_resRules = rJoin (rl_resRules, fn_genMultCycResRules (fpu_madd));
   rl_resRules = rJoinMutuallyExclusive (rl_resRules, fn_genMultCycResRules (fpu_div));
   addRules (rl_resRules);

   rule passResult;
      isNegateFifo.deq();
      let negateResult = isNegateFifo.first();

      rmdFifo.deq();
      let rmode = rmdFifo.first();

      FSingle   v  = tpl_1(resWire);
      FloatingPoint::Exception ex = tpl_2(resWire);
      if (negateResult)
         v = negate( v );
      FloatU res = tagged S v;
      oFifo.enq( tuple2( res, ex ) );
   endrule

   rule rl_reset;
      resetReqsF.deq;
      iFifo.clear;
      oFifo.clear;
      rmdFifo.clear;
      isNegateFifo.clear;
      resetRspsF.enq (?);
   endrule


   // =============================================================
   // INTERFACE
   // ---- Reset
   interface server_reset = toGPServer (resetReqsF, resetRspsF);
   interface server_core = toGPServer ( iFifo, oFifo );
endmodule
endpackage
