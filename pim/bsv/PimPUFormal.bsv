// PimPUFormal.bsv -- formal-only wrapper: mkPimPU with a concrete
// LocalStore.  bsc -verilog cannot generate separate code for a module
// with an interface argument (G0008), so the formal flow instantiates
// this wrapper instead.  The wrapper's ports are the PimPU interface.
package PimPUFormal;

import PimTypes::*;
import PimStages::*;
import PimPU::*;

(* synthesize *)
module mkPimPUFormal(PimPU);
  LocalStore store <- mkLocalStore("generated/program.hex");
  PimPU pu <- mkPimPU(store);
  return pu;
endmodule

endpackage
