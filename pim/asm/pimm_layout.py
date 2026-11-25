"""Runtime-state layouts shared by the reference model and the Bluespec
core (docs/pimm_semantics.md "Runtime state").  They are this project's
design: how the PIM/m firmware laid these out is lost with it.

A goal record is G_ARGS + argn cells:
    +G_LINK    {INT, the next record in the ready queue, or 0}
    +G_STATUS  {INT, shoen << 2 | (READY | SUSPENDED | TAKEN)}: the
               shoen the goal belongs to is the address of its shoen
               record RELATIVE to the load address (so that it fits
               above the two status bits), 0 for the root, which has
               no record: a goal outside every shoen has the plain
               status here
    +G_CODE    {INT, code address}
    +G_ARGN    {INT, number of arguments}
    +G_ARGS..  the arguments
A suspension record is S_SIZE cells, one per (goal, variable) wait:
    +S_NEXT    {INT, the next suspension record on this variable, or 0}
    +S_GOAL    {INT, the goal record}
An unbound variable with goals waiting is {HOOK, its first suspension
record}; without, {UNDF, 0}.  Addresses in cells are absolute.
A shoen record is SH_SIZE cells (docs/pimm_semantics.md "Shoen"; the
handle a register holds is {SHREC, its address}: the tag is 38h SHREC
of PIMOS's debugger/inspector/tagtbl.kl1, what it points at is ours):
    +SH_COUNT   {INT, the shoen's live goals + its live child shoen}
    +SH_STATUS  {INT, DORMANT | STARTED | TERMINATED}
    +SH_PARENT  {INT, the parent's shoen record, or 0 for the root}
    +SH_REPORT  a reference to the unbound tail of the report stream
    +SH_GOAL    {INT, the goal record of the shoen's first goal}:
                parked (SUSPENDED, on no queue and on no variable)
                until start_shoen
    +SH_REDUCTIONS {INT, the reductions of the shoen's goals so far,
                and of its child shoen that have terminated}: added to
                at the end of each of its goals' runs, and a child's
                total is added to its parent's when the child
                terminates (shoen stage 2; 32 bits, so it wraps at
                2**32 reductions: not checked)
    +SH_REMOVE  {INT, 1 if remove_shoen came before the shoen
                terminated, else 0}: it is then removed at termination
    +SH_MASK    {INT, the exception mask create_shoen was given} (shoen
                stage 3): an exception is reported to the innermost
                shoen whose mask AND the exception's tag is not 0
                (PIMOS manual e-shoen.tex:57)
    +SH_RSC_HI, +SH_RSC_LO {INT, the high and low 32 bits of the
                resource LEFT, two's complement: the sum of the shoen's
                add_resource amounts less what the goals of it and of
                every shoen inside it have consumed, 2 a reduction}
                (R7L, 2026-11-25; 0 at creation, VPIM's
                _INIT_SHOEN_RESOURCE, f_shoen_main.psl.c)
    +SH_RSC_FLAGS {INT, bit 0: resource reports disallowed}: clear at
                creation (VPIM's status word starts 0; manual
                e-shoen.tex:179 "A report is normally ready for being
                sent"), set when resource_low is reported, cleared by
                allow_shoen_resource_report
SH_GOAL is the head of a list, linked through G_LINK, of the shoen's
PARKED goals (stage 3): the first goal until start_shoen, and the goals
taken from the ready queue while the shoen, or one above it, is
stopped, or exhausted (no resource left), and start_shoen releases
them all and writes 0 there, as add_shoen_resource does on a started
shoen it gives resource to.
"""
G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS = 0, 1, 2, 3, 4
READY, SUSPENDED, TAKEN = 0, 1, 2
S_NEXT, S_GOAL, S_SIZE = 0, 1, 2
SH_COUNT, SH_STATUS, SH_PARENT, SH_REPORT, SH_GOAL, SH_SIZE = 0, 1, 2, 3, 4, 11
SH_REDUCTIONS, SH_REMOVE = 5, 6
SH_MASK = 7
SH_RSC_HI, SH_RSC_LO, SH_RSC_FLAGS = 8, 9, 10
RSC_REPORT_DISALLOWED = 1
# REMOVED: terminated, then removed (remove_shoen): the report stream is
# closed and the record is not used again
DORMANT, STARTED, TERMINATED, REMOVED = 0, 1, 2, 3
# STOPPED: stop_shoen on a started shoen (stage 3); start_shoen starts it
# again.  An aborted shoen is TERMINATED at once (its `aborted` comes
# first on the report stream): a goal found under a TERMINATED or
# REMOVED shoen is discarded when it is taken from the ready queue
STOPPED = 4
# The report stream's integer codes that the models emit.  PIM/m-sourced:
# the image's shoen:report/2 (cell 15818) translates 8 to `started` and
# 12 to `terminated` (PIMOS macro/pimos/pimos/pimos.vmac:177-199 agrees),
# 10 to `statistics_started`, {9, H, L} to `statistics(H, L)` and
# {14, H, L} to `return_resource(H, L)`.
REPORT_STARTED, REPORT_TERMINATED = 8, 12
REPORT_STATISTICS_STARTED, REPORT_STATISTICS, REPORT_RETURN_RESOURCE = 10, 9, 14
# Stage 3: 1 `aborted`, 11 `stopped` and {2, Kind, Info, NewCode,
# NewArgv} `exception(..)`, the same report/2 and pimos.vmac; Kind is
# the firmware's exception number (pimos.vmac:331-349
# exception_code#..: 9 reduction_failure, 16 raised), the language tag
# of number n is 1 << (16 + n) (manual e-shoen.tex table "Exception Tag
# Bit Positions"; VPIM f_ConvertExceptionNumberToTag agrees)
REPORT_ABORTED, REPORT_EXCEPTION, REPORT_STOPPED = 1, 2, 11
# add_shoen_resource (2026-11-24): 5 `resource_added` (pimos.vmac, the
# same table; manual e-shoen.tex, the ACK of add_resource)
REPORT_RESOURCE_ADDED = 5
# allow_shoen_resource_report (2026-11-24): 7 `resource_report_allowed`
# (pimos.vmac, the same table; manual e-shoen.tex 174-180, 254-262)
REPORT_RESOURCE_REPORT_ALLOWED = 7
# resource_low (R7L, 2026-11-25): 6 (pimos.vmac:185 shoen#resource_low;
# the image's report/2 and kernel/builtin/shoen.kl1:220 translate it)
REPORT_RESOURCE_LOW = 6
EXC_REDUCTION_FAILURE, EXC_RAISED = 9, 16

ADDR_BITS = 27                  # memory size in cells = 1 << ADDR_BITS
MEMORY_CELLS = 1 << ADDR_BITS
HEAP = 0x8000                   # first heap cell, from the load address
