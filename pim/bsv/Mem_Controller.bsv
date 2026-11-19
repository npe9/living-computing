// Mem_Controller.bsv -- raw-memory width types for the PIM's SDRAM bridge.
//
// The SDRAM controller was taken from the Flute ULX3S work, where the
// raw-memory port is 256 bits wide at a 64-bit granule address.  Only
// those two widths are needed here; the rest of Flute's Mem_Controller
// package (fabric address decoding, cache-line helpers) is not part of
// the PIM model.

package Mem_Controller;

typedef 256 Bits_per_Raw_Mem_Word;
typedef Bit#(Bits_per_Raw_Mem_Word) Raw_Mem_Word;

typedef 64 Bits_per_Raw_Mem_Addr;
typedef Bit#(Bits_per_Raw_Mem_Addr) Raw_Mem_Addr;

endpackage
