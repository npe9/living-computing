// PimLink.bsv -- point-to-point link between two PimNU ports.
//
// Model-derived: the PIM/m sources document the 9-bit packet byte, the
// FIFO output buffers, and the one-byte-per-four-cycles rate enforced
// by the NU, but they do not give the crossbar arbitration order or
// the 2-bit direction encoding (M92 p.427).  This module therefore
// bridges one output port to one input port with no routing decision;
// routing and arbitration are the responsibility of the NU or the mesh
// network, not the wire.

package PimLink;

import PimNU::*;

module mkPimLink#(PimNUOutPort src, PimNUInPort dst)(Empty);
  rule move (src.get() matches tagged Valid .b &&& dst.ready());
    dst.put(b);
    src.deq();
  endrule
endmodule

endpackage
