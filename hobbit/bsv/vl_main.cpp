// vl_main.cpp -- the Verilator driver for a bsc-generated testbench
// (bsv/run_p9host_vl.sh; bsv/run_golden.sh with HOBBIT_SIM=verilator).
//
// bsc -verilog writes the testbench as a module with only CLK and RST_N
// (active low).  This does what bsc's own Verilog driver does
// ($BLUESPECDIR/Verilog/main.v): reset across the first rising edge,
// release it, then clock until the design calls $finish.  bsc puts every
// system task and imported (DPI-C) call in an `always @(negedge CLK)`
// block, in the rules' schedule order, and the state updates in
// `always @(posedge CLK)`; so each clock is two evaluations, the falling
// edge (the $display lines and C calls) and then the rising edge.
//
// Build with -DVL_TOP=VmkP9HostTb (the Verilated class),
// -DVL_TOP_H='"VmkP9HostTb.h"' and -DVL_USER_FINISH.
//
// $finish.  Bluesim stops at the $finish: no rule after it in that clock
// runs.  Verilator's default $finish only sets a flag, and the rest of the
// negedge block still runs (one more HRI line after P9HOST EXIT, observed
// 2026-11-23), and it prints "- file:line: Verilog $finish".  So
// vl_finish here flushes and exits at once.
//
// Exit status.  Verilog's $finish(n) takes a *diagnostic level*, not an
// exit status, and Verilator drops it; Bluesim exits with n, and
// bsv/run_p9host.sh treats a non-zero status as a failed run.  With
// -DVL_P9HOST the driver recomputes P9HostTb.bsv's `ok` -- the machine
// reached exits (p9h_poll returned 2) and the recording is fully served
// (p9h_finished() == 1) -- by wrapping p9h_poll: p9host.c is compiled with
// -Dp9h_poll=p9h_poll_c, and the p9h_poll the Verilated model imports is
// the one below.  p9host.c itself is unchanged.  Without VL_P9HOST the
// status is 0, as for the golden testbenches, whose $finish carries none.
//
// $VL_MAXCLOCKS (default 0, no limit) stops a run that never calls
// $finish, with status 4.  A build with --trace writes vl.vcd for clocks
// [$VL_TRACE_FROM, $VL_TRACE_TO); the falling edge of clock c is at time
// 2c+1, the rising edge at 2c+2.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <memory>

#include "verilated.h"
#include VL_TOP_H
#if VM_TRACE
#include "verilated_vcd_c.h"
static VerilatedVcdC *tfp;
#endif

#ifdef VL_P9HOST
extern "C" uint32_t p9h_poll_c(uint32_t sp);
extern "C" uint32_t p9h_finished(void);
static bool reached_exits;
extern "C" uint32_t p9h_poll(uint32_t sp) {
  const uint32_t r = p9h_poll_c(sp);
  if (r == 2) reached_exits = true;
  return r;
}
#endif

static int finish_status() {
#ifdef VL_P9HOST
  return (reached_exits && p9h_finished() == 1) ? 0 : 1;
#else
  return 0;
#endif
}

void vl_finish(const char *filename, int linenum, const char *hier) {
  (void)filename;
  (void)linenum;
  (void)hier;
#if VM_TRACE
  if (tfp) tfp->close();
#endif
  std::fflush(stdout);
  std::fflush(stderr);
  std::exit(finish_status());
}

double sc_time_stamp() { return 0; }

int main(int argc, char **argv) {
  const std::unique_ptr<VerilatedContext> ctx{new VerilatedContext};
  ctx->commandArgs(argc, argv);
  VL_TOP *top = new VL_TOP{ctx.get(), "TOP"};

  const char *m = std::getenv("VL_MAXCLOCKS");
  const uint64_t maxclocks = m ? std::strtoull(m, nullptr, 10) : 0;
  uint64_t clocks = 0;

#if VM_TRACE
  ctx->traceEverOn(true);
  tfp = new VerilatedVcdC;
  top->trace(tfp, 99);
  tfp->open("vl.vcd");
  const char *tf = std::getenv("VL_TRACE_FROM");
  const char *tt = std::getenv("VL_TRACE_TO");
  const uint64_t tfrom = tf ? std::strtoull(tf, nullptr, 10) : 0;
  const uint64_t tto = tt ? std::strtoull(tt, nullptr, 10) : ~0ull;
#define DUMP(t) \
  do { if (clocks >= tfrom && clocks < tto) tfp->dump(t); } while (0)
#else
#define DUMP(t) do { } while (0)
#endif

  // main.v: RST_N = 0, CLK = 1 (the reset edge), RST_N = 1 before the
  // first falling edge.
  top->CLK = 0;
  top->RST_N = 0;
  top->eval();
  top->CLK = 1;
  top->eval();
  top->RST_N = 1;
  top->eval();

  for (;;) {
    top->CLK = 0;
    top->eval();
    DUMP(2 * clocks + 1);
    top->CLK = 1;
    top->eval();
    DUMP(2 * clocks + 2);
    if (maxclocks && ++clocks >= maxclocks) {
#if VM_TRACE
      tfp->close();
#endif
      std::fflush(stdout);
      std::fprintf(stderr, "vl_main: no $finish in %llu clocks\n",
                   (unsigned long long)maxclocks);
      return 4;
    }
  }
}
