#!/bin/sh
# PIM/m regression suite: assembler, ISA table, Bluesim smoke and
# testbenches, formal BMC.
# Run from anywhere; the script changes to its own directory.
set -eu
cd "$(dirname "$0")"

echo "=== pimasm selftest ==="
python3 asm/pimasm.py --selftest

echo "=== ISA table check ==="
python3 asm/gen_isa_table.py --check

echo "=== PIMOS object-set census (every .sav decodes) ==="
python3 asm/census.py --check

echo "=== PIM/m to PDSS instruction name map (class sizes pinned) ==="
python3 asm/namemap.py --check

echo "=== IPL image pimm_ipl.kbn (every cell placed) ==="
python3 asm/kbn.py --check
python3 asm/kbndis.py --check

echo "=== runtime inventory (groups and sub-functions pinned) ==="
python3 asm/inventory.py --check

echo "=== built-in operand directions, from the PIMOS compiler source ==="
python3 asm/bltdir.py --check
python3 asm/pimm_stubs.py --check

echo "=== PDSS port: a KL1 program compiled and run on the 1992 KL1-B emulator ==="
ref/pdss/test.sh

echo "=== PIM/m reference model: a PIMOS predicate run from the IPL image ==="
python3 ref/pimm/test_jtoa.py

echo "=== PIM/m core (Bluespec) in lockstep with the reference model ==="
bsv/run_pimm_lockstep.sh

echo "=== Bluesim smoke ==="
bsv/run_smoke.sh

echo "=== Bluesim negative-opcode testbench ==="
bsv/run_neg_tb.sh

echo "=== Bluesim KL1-B execution testbench ==="
bsv/run_kl1b_tb.sh

echo "=== Bluesim NU testbench ==="
bsv/run_nu_tb.sh

echo "=== Bluesim link testbench ==="
bsv/run_link_tb.sh

echo "=== Bluesim routed NU testbench ==="
bsv/run_nu_routed_tb.sh

echo "=== Bluesim mesh testbench ==="
bsv/run_mesh_tb.sh

echo "=== Bluesim SDRAM store testbench ==="
bsv/run_sdram_tb.sh

echo "=== formal BMC (fixed PASS, buggy FAIL) ==="
bsv/formal/run_formal.sh

echo "=== pim suite: PASS ==="
