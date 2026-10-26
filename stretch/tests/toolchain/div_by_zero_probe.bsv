package P;
(* synthesize *)
module mkP(Empty);
  Reg#(Bit#(96)) d <- mkReg(0);
  Reg#(Bool) done  <- mkReg(False);
  rule r (!done);
    done <= True;
    $display("entered, d=%0d", d);
    if (d == 0) begin
      $display("GUARDED branch");
    end else begin
      Bit#(96) q = 96'd1000 / d;
      $display("ELSE branch, q=%0d", q);
    end
  endrule
  rule fin (done); $finish(0); endrule
endmodule
endpackage
