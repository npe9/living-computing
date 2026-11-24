// PimmSdTypes.bsv -- the block interface between the FEP emulator and a
// card: 512-byte block reads, nothing else.  ALL OURS.
//
// A request names a block (a 512-byte block number on the card, as
// pim/tools/mkfepcard.py lays the image out).  The answer is the block's
// 512 bytes in order, `last` on the 512th; or one byte with `err` and
// `last` both set if the block cannot be read (past the end of the
// image, a card that does not answer, a timeout).  There is no write:
// nothing behind this interface can change a card.
//
// Two servers implement it: mkPimmSdBlock (PimmSdBlock.bsv, the ULX3S
// microSD slot in SPI mode, for the bitstream) and mkPimmSdBlockFile
// (PimmSdBlockFile.bsv, a host image file through BDPI, Bluesim only).
// The emulator holds the matching Client, so the BDPI package is never in
// a hierarchy that is synthesized.

package PimmSdTypes;

import ClientServer::*;

typedef 512 SdBlockBytes;

typedef struct {
   Bit#(32) block;
} SdBlockReq deriving (Bits, Eq, FShow);

typedef struct {
   Bit#(8) data;
   Bool    last;
   Bool    err;
} SdBlockByte deriving (Bits, Eq, FShow);

typedef Server#(SdBlockReq, SdBlockByte) SdBlockServer;
typedef Client#(SdBlockReq, SdBlockByte) SdBlockClient;

endpackage
