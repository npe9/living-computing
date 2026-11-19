// PimMesh.bsv -- parameterized 2-D mesh of routed PIM/m network units.
//
// Documented facts (M92 = Nakashima et al., FGCS '92 vol. 1, printed
// pages 425-435; see docs/pim_architecture.md section 1):
//
//   * A PIM/m system is a 16 x 16 mesh of up to 256 PEs; a cabinet is
//     an 8 x 4 sub-mesh and adjacent cabinets are wired together.
//   * Each NU switches four adjacent-PE channel pairs plus the CPU pair
//     (a 5 x 5 crossbar) and transmits one packet byte per four machine
//     cycles, using FIFO output buffers and back-pressure.
//   * A packet byte is 9 bits (8 data plus a mark bit), routing uses a
//     RAM path table indexed by destination PE with a 2-bit direction
//     code, and the read buffer raises an interrupt on the packet tail
//     (M92 p.427).
//
// MODEL -- none of the following is in the sources:
//
//   * Topology and PE numbering.  The mesh is dim x dim with `dim` a
//     numeric type parameter, so the testbench writes PimMesh#(4).
//     PE = y*dim + x, row-major, with (0,0) at the north-west corner:
//     x grows east, y grows south.  Port numbering is 0 = North,
//     1 = East, 2 = South, 3 = West, 4 = CPU.
//   * Direction encoding.  A route-table entry is an absolute output
//     port selector: 0 = North, 1 = East, 2 = South, 3 = West.
//     "Arrived" is NOT a table code; mkPimNURouted sends a byte to the
//     CPU port (4) when the destination PE is the NU's own PE.
//   * Route table.  Entry [d] for destination PE d is deterministic XY
//     routing from this NU's (x,y): East if destX > x, West if
//     destX < x, else South if destY > y, else North.  The own-PE
//     entry and entries >= dim*dim are don't-cares; neither is ever
//     consulted (the own-PE comparison wins, and no PE has a number
//     >= dim*dim).
//   * Arbitration is the routed crossbar's fixed priority, lowest
//     input-port index wins (PimNURouted.bsv).  The source gives no
//     arbitration order.
//   * Edge tie-off.  Every mesh-edge output port drains into a sink
//     that always dequeues when a byte is valid, so a packet routed
//     off the edge (only possible for a destination outside the mesh)
//     cannot wedge the fabric.  An edge input port has no driver:
//     nothing can put into it, so it is permanently empty.  A tiling
//     wrapper would replace these ties-offs with cabinet links.
//
// The topology, numbering, route-table encoding, arbitration order and
// edge behaviour above are model choices, not documented facts.

package PimMesh;

import Vector::*;
import PimNU::*;
import PimLink::*;
import PimNURouted::*;

// Model choice: the default dimension used by the testbench.  The mesh
// itself is parameterized by the numeric type d, so PimMesh#(MeshDim)
// is a 4 x 4 mesh of 16 PEs.
typedef 4 MeshDim;

interface PimMesh#(numeric type d);
  // CPU-side injection port of every PE (NU port 4, in direction).
  interface Vector#(TMul#(d, d), PimNUInPort) cpuIn;
  // CPU-side receive port of every PE (NU port 4, out direction).
  interface Vector#(TMul#(d, d), PimNUOutPort) cpuOut;
  // packetTail()[pe] is the read-buffer tail interrupt of PE pe.
  method Vector#(TMul#(d, d), Bool) packetTail();
endinterface

// XY route table for the NU at (x,y), indexed by destination PE.
// MODEL: see the header comment for the encoding.
function Vector#(256, Direction) xyRouteTable(Integer pe, Integer dim);
  Vector#(256, Direction) t = replicate(2'd0);
  Integer x = pe % dim;
  Integer y = pe / dim;
  for (Integer dst = 0; dst < 256; dst = dst + 1) begin
    Integer dx = dst % dim;
    Integer dy = dst / dim;
    Direction dir = 2'd0;               // North; also the don't-cares
    if (dx > x)      dir = 2'd1;        // East
    else if (dx < x) dir = 2'd3;        // West
    else if (dy > y) dir = 2'd2;        // South
    t[dst] = dir;
  end
  return t;
endfunction

// An unconnected mesh-edge output drains: a one-byte buffer that is
// always dequeued keeps the NU making progress, so an off-mesh packet
// disappears instead of wedging the fabric.  MODEL.
module mkPimMeshSink#(PimNUOutPort src)(Empty);
  rule drain (src.get() matches tagged Valid .b);
    src.deq();
  endrule
endmodule

module mkPimMesh(PimMesh#(d));
  Integer dim = valueOf(d);

  // One routed NU per PE, each with its own XY route table.
  Vector#(TMul#(d, d), PimNU) nus = newVector;
  for (Integer pe = 0; pe < dim * dim; pe = pe + 1) begin
    let nu <- mkPimNURouted(fromInteger(pe), xyRouteTable(pe, dim));
    nus[pe] = nu;
  end

  // Adjacent-PE links.  Each neighbour pair gets two one-way links:
  // East of (x,y) into West of (x+1,y), and the reverse.  The same for
  // South/North.  MODEL: topology.
  for (Integer y = 0; y < dim; y = y + 1)
    for (Integer x = 0; x + 1 < dim; x = x + 1) begin
      Integer i = y * dim + x;
      Empty east  <- mkPimLink(nus[i].out[1], nus[i + 1].in_[3]);
      Empty west  <- mkPimLink(nus[i + 1].out[3], nus[i].in_[1]);
    end

  for (Integer y = 0; y + 1 < dim; y = y + 1)
    for (Integer x = 0; x < dim; x = x + 1) begin
      Integer i = y * dim + x;
      Empty south <- mkPimLink(nus[i].out[2], nus[i + dim].in_[0]);
      Empty north <- mkPimLink(nus[i + dim].out[0], nus[i].in_[2]);
    end

  // Mesh-edge outputs drain (MODEL: tie-off).  Separate loops keep the
  // module instantiations unconditional; each corner is covered by the
  // two loops for its two outward directions.
  for (Integer x = 0; x < dim; x = x + 1) begin
    Empty n <- mkPimMeshSink(nus[x].out[0]);                    // north
    Empty s <- mkPimMeshSink(nus[(dim - 1) * dim + x].out[2]);  // south
  end
  for (Integer y = 0; y < dim; y = y + 1) begin
    Empty w <- mkPimMeshSink(nus[y * dim].out[3]);              // west
    Empty e <- mkPimMeshSink(nus[y * dim + dim - 1].out[1]);    // east
  end

  // Expose the CPU pair of every PE.
  Vector#(TMul#(d, d), PimNUInPort) cpuInVec = newVector;
  Vector#(TMul#(d, d), PimNUOutPort) cpuOutVec = newVector;
  Vector#(TMul#(d, d), Bool) tailVec = newVector;
  for (Integer pe = 0; pe < dim * dim; pe = pe + 1) begin
    cpuInVec[pe] = nus[pe].in_[4];
    cpuOutVec[pe] = nus[pe].out[4];
    tailVec[pe] = nus[pe].packetTail();
  end

  interface cpuIn = cpuInVec;
  interface cpuOut = cpuOutVec;
  method Vector#(TMul#(d, d), Bool) packetTail() = tailVec;
endmodule

endpackage
