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
python3 asm/psdpim.py --check
python3 asm/mekbn.py --check
python3 asm/pu_cfg.py --check
python3 asm/pu_sysinit.py --check
python3 asm/pu_smt.py --check

echo "=== held KL1 microprogram executed (ref/pu, rung U1 of docs/pu_microcode_plan.md) ==="
python3 ref/pu/check_pu.py
echo "=== held KL1 microprogram on a whole program (ref/pu/u2_append.py, rung U2: furthest point, not reached) ==="
python3 ref/pu/u2_append.py
echo "=== held KL1 microprogram on a multi-goal program, the scheduler held (ref/pu/u3_goals.py, rung U3 first step) ==="
python3 ref/pu/u3_goals.py

echo "=== PSI side: the Librarian's loader, .ptf templates to class objects (TM-388 cases, known plaintext) ==="
python3 -I psi/test_librarian.py

echo "=== PSI side: the KL0 interpreter on compiled .ptf code (opcodes from known plaintext, convert/3 against PIMOS) ==="
python3 -I psi/test_kl0.py
python3 -I psi/fepread/check.py

echo "=== PSI side: the ESP compiler (ours) against paragraph.ptf, and the SIMPOS stand-ins ==="
python3 -I psi/test_espc.py

echo "=== PSI side: the held SIMPOS FEP logs into PIMOS (step 3n; the live run's tape replayed, the live run opt-in) ==="
python3 -I psi/test_fep_bridge.py

echo "=== PSI side: MENDELS (IFS No.61), its KL1 half on PIMOS and its ESP half on the PSI, linked by string I/O (the live run's tape replayed, the live run opt-in) ==="
python3 -I psi/test_mendels.py

echo "=== PSI side: the SIMPOS top level, the debugger's listener starts a held program in a new process (step 3o) ==="
python3 -I psi/test_boot_route.py

echo "=== PSI side: window M11's live view, the stand-in SIMPOS on tools/winview (recorded sessions = the scripted pins) ==="
python3 -I psi/test_live.py

echo "=== PDSS port: a KL1 program compiled and run on the 1992 KL1-B emulator ==="
ref/pdss/test.sh

echo "=== PIM/m reference model: a PIMOS predicate run from the IPL image ==="
python3 ref/pimm/test_jtoa.py

echo "=== PIM/m reference model alone: the IPL's own SCSI file service (prototype) ==="
python3 ref/pimm/ref_scsi.py

echo "=== PIM/m reference models alone, one PE and several: wait_value on modules, codes and shoen handles; get_heap_size; X = X, @node, set_heap_alert; @priority of 12 arguments, list, unification_failure ==="
python3 ref/pimm/ref_wait_value.py
python3 ref/pimm/ref_node_alert.py
python3 ref/pimm/ref_prio_list.py

echo "=== PIM/m reference model, several PEs (rung M1, docs/multi_pe.md): PIMOS's seqgc and gc on 1, 2, 4 PEs ==="
python3 ref/pimm/m1_gc.py
echo "=== PIM/m reference model, several PEs (rung M2, docs/multi_pe.md): %read, %answer_value, structures across PEs; PIMOS's heap monitors on 1, 2, 4 PEs ==="
python3 ref/pimm/m2_read.py
echo "=== PIM/m reference model, several PEs (rung M3, docs/multi_pe.md): white and black tables, WEC, collections with live tables ==="
python3 ref/pimm/m3_gc.py
echo "=== PIM/m reference model, several PEs (rung M4, docs/multi_pe.md): the shoen across PEs, foster parents, WTC, %terminated, control and statistics ==="
python3 ref/pimm/m4_shoen.py
echo "=== IFS applications on PIMOS (docs/ifs_apps.md): the pinned outcome table, the printed results in their archives, the runner's injections ==="
python3 -I ref/pimm/ifs_sweep.py --check

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

echo "=== Bluesim FEP emulator against ref/pimm/fep.py (image file and SPI reader) ==="
bsv/run_fepemu.sh

echo "=== formal BMC (fixed PASS, buggy FAIL) ==="
bsv/formal/run_formal.sh

# --- window framebuffer box (window_hardware_plan.md H0/H1) ---
echo "=== Bluesim window framebuffer box against psi/winfb.py (PBM lockstep) ==="
bsv/run_win_tb.sh

echo "=== pim suite: PASS ==="
