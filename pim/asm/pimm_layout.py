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
"""
G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS = 0, 1, 2, 3, 4
READY, SUSPENDED, TAKEN = 0, 1, 2
S_NEXT, S_GOAL, S_SIZE = 0, 1, 2
SH_COUNT, SH_STATUS, SH_PARENT, SH_REPORT, SH_GOAL, SH_SIZE = 0, 1, 2, 3, 4, 7
SH_REDUCTIONS, SH_REMOVE = 5, 6
# REMOVED: terminated, then removed (remove_shoen): the report stream is
# closed and the record is not used again
DORMANT, STARTED, TERMINATED, REMOVED = 0, 1, 2, 3
# The report stream's integer codes that the models emit.  PIM/m-sourced:
# the image's shoen:report/2 (cell 15818) translates 8 to `started` and
# 12 to `terminated` (PIMOS macro/pimos/pimos/pimos.vmac:177-199 agrees),
# 10 to `statistics_started`, {9, H, L} to `statistics(H, L)` and
# {14, H, L} to `return_resource(H, L)`.
REPORT_STARTED, REPORT_TERMINATED = 8, 12
REPORT_STATISTICS_STARTED, REPORT_STATISTICS, REPORT_RETURN_RESOURCE = 10, 9, 14

ADDR_BITS = 27                  # memory size in cells = 1 << ADDR_BITS
MEMORY_CELLS = 1 << ADDR_BITS
HEAP = 0x8000                   # first heap cell, from the load address
