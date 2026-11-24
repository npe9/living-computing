// PimmFepEmuSpiTb.bsv -- the FEP emulator bench (PimmFepEmuTb.bsv) with
// the card behind the real reader: mkPimmSdBlock (SPI mode, the module the
// board top synthesizes) wired pin to pin to mkPimmSdCardModel over the
// same image file.  ALL OURS.  Two cards: a block-addressed version 2
// card (SDHC: CMD17 takes the block number) and a byte-addressed version
// 1 card (CMD8 illegal, CMD16 512, CMD17 takes the block times 512).  The
// clock divisors are the board's but for the slow half period (4, not
// 32) and no power-up wait, to keep the run short; the reader's logic is
// the same either way.

package PimmFepEmuSpiTb;

import PimmSdTypes::*;
import PimmSdBlock::*;
import PimmSdCardModel::*;
import PimmFepEmuTb::*;

module mkSpiCard#(Bool blockAddressed, Bool version1)(SdBlockServer);
   PimmSdBlock     sd   <- mkPimmSdBlock(0, 4, 2);
   PimmSdCardModel card <- mkPimmSdCardModel(blockAddressed, version1, 3, 5);
   rule rl_pins;
      card.pins(sd.sd_clk, sd.sd_cs_n, sd.sd_mosi);
      sd.sd_miso(card.miso);
   endrule
   return sd.blocks;
endmodule

(* synthesize *)
module mkPimmFepEmuSpiTb(Empty);
   SdBlockServer card <- mkSpiCard(True, False);
   Empty b <- mkPimmFepEmuBench(card);
endmodule

(* synthesize *)
module mkPimmFepEmuSpiSdscTb(Empty);
   SdBlockServer card <- mkSpiCard(False, True);
   Empty b <- mkPimmFepEmuBench(card);
endmodule

endpackage
