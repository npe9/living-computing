# Toolchain behaviour this project has had to work around

Small self-contained probes. They are NOT in `run_tests.sh`: they
test the compiler, not the model, and a suite that fails when the
toolchain is upgraded is a suite that gets ignored.

## `div_by_zero_probe.bsv` — a guarded division by zero is not guarded

**Found 2026-10-25**, by `decks/vfl_divide.strap`'s zero-divisor
check on its first run, which died with

```
./run_program.sh: line 39: 52936 Floating point exception: 8   "./StretchVflDivideTb_sim"
```

The VFL `/` arm is written the way printed p.70 states the rule —
"this indicator is turned on if the binary divisor is zero. **The
division is not attempted**" — so the quotient is computed in the
`else` of a guard and cannot be used when the divisor is zero.

**That is not enough, and the way it is not enough differs with the
operand width.** The probe is one rule, a register holding zero that
is never written, and `if (d == 0)` guarding `1000 / d`:

| width | result |
| --- | --- |
| `Bit#(32)` | exit 0, **takes the ELSE branch**, prints `q=0` |
| `Bit#(64)` | exit 0, **takes the ELSE branch**, prints `q=0` |
| `Bit#(96)` | **exit 136 (SIGFPE), no output at all** |
| `Bit#(128)` | **exit 136 (SIGFPE), no output at all** |

Identical on Homebrew bsc **2026.01** and on `~/src/bsc-cursor-ergo`
**2026.07-46-g91bdcade**, so it is longstanding behaviour and not a
regression in either.

**Two separate defects.** Above 64 bits Bluesim aborts the whole
simulation on a value the design never observes, and does it before
ANY action in the rule executes — the guard's own `$display` never
printed. At or below 64 bits it is worse: the **branch condition is
miscompiled**. `d == 0` contains no division, and it selects the
wrong arm.

**Two controls prove the `if` itself is sound**, and they are the
reason this is written down as a toolchain note rather than a
mystery:

```
Bit#(32) q = 1000 + d;        -> GUARDED branch  (correct)
Bit#(32) q = 1000 / (d + 7);  -> GUARDED branch  (correct)
Bit#(32) q = 1000 / d;        -> ELSE branch     (wrong)
```

Only a divisor the compiler can prove is zero breaks it.

### What the model does about it

`StretchExecute.bsv`'s `/` arm divides by `(dsr == 0) ? 1 : dsr` and
discards the result on the zero path. **This is our fix to make, not
theirs**: division by zero is undefined in BSV, and a guard stops a
value being CONSUMED, never computed — in hardware the divider is
always instantiated. Relying on the guard was relying on undefined
behaviour.

It is also the more faithful model. The manual does not say the
machine computes a quotient and throws it away; it says the division
is not attempted and ZD is turned on. That is an indicator decision,
and keeping it out of the arithmetic is where it belongs.

### Reproducing

```sh
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
export PATH=/opt/homebrew/Cellar/bsc/2026.01/bin:$PATH
cd $(mktemp -d) && cp <repo>/tests/toolchain/div_by_zero_probe.bsv P.bsv
bsc -sim -bdir . -simdir . -info-dir . -g mkP -u P.bsv
bsc -sim -bdir . -simdir . -e mkP -o p
./p; echo "exit=$?"      # 136 = SIGFPE
```

Edit the two `Bit#(96)` occurrences to `Bit#(32)` for the
wrong-branch form.
